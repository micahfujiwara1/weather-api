import polars as pl
import pathlib
from models import Weather, YieldData, WeatherAnalysis, db
from datetime import datetime
import logging


__PROJECT_DIR__: pathlib.Path = pathlib.Path(__file__).parent.parent
WX_DATA: pathlib.Path = __PROJECT_DIR__ / 'wx_data'
YLD_DATA: pathlib.Path = __PROJECT_DIR__ / 'yld_data' / 'US_corn_grain_yield.txt'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wx_consolidation_cleanse(df: pl.DataFrame, weather_station_id:str) -> pl.DataFrame:
    """
    Cleanses weather data from a specific weather station

    Args:
        df (pl.DataFrame): the dataframe containing raw weather data.
        weather_station_id (str): the ID of the weather station

    Returns:
        pl.DataFrame: the cleansed dataframe for designated weather station
    """
    df = df.with_columns(weather_station_id = pl.lit(weather_station_id).cast(pl.String),
                         date = pl.col('date').cast(pl.String).str.to_date(r'%Y%m%d'),
                         max_temp = pl.col('max_temp').str.strip_chars().cast(pl.Int32),
                         min_temp = pl.col('min_temp').str.strip_chars().cast(pl.Int32),
                         precipitation = pl.col('precipitation').str.strip_chars().cast(pl.Int32))


    df = df.with_columns(
        pl.when(pl.col(pl.Int32) == -9999)
        .then(None)
        .otherwise(pl.col(pl.Int32))
        .name.keep()
    )
    return df


def wx_consolidation(folderpath:str) -> pl.DataFrame:
    """
    Consolidates weather data from multiple files in a given folder

    Args:
        folderpath (str): The path to the folder containing weather data files

    Returns:
        pl.DataFrame: The consolidated weather dataframe with cleaned and combined data from all files in the folerpath    

    Raises:
        FileNotFoundError: If the specified folder does not exist.
        ValueError: If there is an issue reading or processing any of the files in the folder.
    """
    df: list[pl.DataFrame] = []
    
    for file in folderpath.iterdir():
        if not folderpath.exists() or not folderpath.is_dir():
            raise FileNotFoundError(f"The folder path '{folderpath}' does not exist or is not a directory.")

        if file.is_file():
            weather_station_id: str = file.name.replace('.txt', '')
            headers: list = ["date", "max_temp", "min_temp", "precipitation"]
            temp_df = pl.read_csv(file, separator='\t', new_columns = headers)
            temp_df = wx_consolidation_cleanse(temp_df, weather_station_id)
            
            df.append(temp_df)

    if not df:
        raise ValueError("No valid weather data files found in the specified folder.")
    
    wx_df = pl.concat(df)
    return wx_df


def yld_consolidation_cleanse(df: pl.DataFrame) -> pl.DataFrame:
    """
    Cleanses yield data.

    Args:
        df (pl.DataFrame): The DataFrame containing raw yield data.

    Returns:
        pl.DataFrame: The cleansed DataFrame.
    """
    df = df.with_columns(year = pl.col('year').cast(pl.Int32),
                         yield_amount = pl.col('yield_amount').cast(pl.Int32))
    
    df = df.with_columns(
        pl.when(pl.col(pl.Int32) == -9999)
        .then(None)
        .otherwise(pl.col(pl.Int32))
        .name.keep()
    )

    return df


def yld_consolidation(file:str) -> pl.DataFrame:
    """
    Reads in yield data from a file.

    Args:
        file (str): The path to the file containing yield data.

    Returns:
        pl.DataFrame: The consolidated yield data DataFrame.
    """
    headers: list = ["year", "yield_amount"]
    df = pl.read_csv(file, separator='\t', new_columns=headers)
    yld_df = yld_consolidation_cleanse(df)
    
    return yld_df



def push_raw_data(wx_df: pl.DataFrame | None = None, yld_df: pl.DataFrame | None = None) -> tuple[int, int]:
    """
    Pushes raw weather and yield data into the database.

    Args:
        wx_df (pl.DataFrame | None): The DataFrame containing weather data.
        yld_df (pl.DataFrame | None): The DataFrame containing yield data.

    Returns:
        tuple[int, int]: A tuple containing the number of new weather records ingested and the number of new yield records ingested.

    Raises:
        Exception: If there is an error during the database operations.
    """
    try:
        num_wx_records = num_yld_records = 0
        
        if wx_df is not None:
            weather_records = db.session.query(Weather).all()

            existing_weather = {}

            for row in weather_records:
                key = (row.weather_station_id, row.date)
                existing_weather[key] = row

            new_weather_records = []
            for row in wx_df.iter_rows():
                if (row[4], row[0]) not in existing_weather:
                    weather = Weather(
                        weather_station_id=row[4],
                        date=row[0],
                        max_temp=row[1],
                        min_temp=row[2],
                        precipitation=row[3]
                    )
                    new_weather_records.append(weather)
            db.session.bulk_save_objects(new_weather_records)
            db.session.commit()
            logger.info("Weather data ingestion complete")
            num_wx_records = len(new_weather_records)
        
        if yld_df is not None:
            yield_records = db.session.query(YieldData).all()

            existing_yield_records = {}

            for row in yield_records:
                key = (row.year)
                existing_yield_records[key] = row

            new_yield_records = []
            for row in yld_df.iter_rows():
                if (row[0]) not in existing_yield_records:
                    yield_data = YieldData(
                        year=row[0],
                        yield_amount=row[1]
                    )
                    new_yield_records.append(yield_data)
            db.session.bulk_save_objects(new_yield_records)
            db.session.commit()
            logger.info("Yield Data ingestion complete")
            num_yld_records = len(new_yield_records)

    except Exception as e:
        logger.error(f"Error: {e}")

    return num_wx_records, num_yld_records



def weather_analysis(wx_df: pl.DataFrame) -> pl.DataFrame:
    """
    Analyzes weather data to calculate statistics.

    Args:
        wx_df (pl.DataFrame): The DataFrame containing weather data.

    Returns:
        pl.DataFrame: DataFrame containing analyzed weather data with statistics (average max temp, average min temp, accumulated precipitation).
    """
    df = wx_df.with_columns((
        pl.col("date").dt.year().alias('year'),
        pl.col('precipitation') * .01) 
        )

    df = df.group_by('weather_station_id', 'year').agg([
        pl.mean('max_temp').cast(pl.Float32).round().alias('avg_max_temp_celsius'),
        pl.mean('min_temp').cast(pl.Float32).round().alias('avg_min_temp_celsius'),
        pl.sum('precipitation').cast(pl.Float32).round().alias('accumulated_precipitation_cm')
    ])

    return df


def push_weather_analysis(wx_analysis_df: pl.DataFrame) -> int:
    """
    Pushes weather analysis data into the database.

    Args:
        wx_analysis_df (pl.DataFrame): The DataFrame containing analyzed weather data.

    Returns:
        int: The number of new weather analysis records ingested.

    Raises:
        Exception: If there is an error during the database operations.
    """
    try:
        num_analysis_records = 0
        if wx_analysis_df is not None:
            analysis_records = db.session.query(WeatherAnalysis).all()

            existing_analysis = {}

            for row in analysis_records:
                key = (row.weather_station_id, row.year)
                existing_analysis[key] = row

            new_analysis_records = []
            for row in wx_analysis_df.iter_rows():
                if (row[0], row[1]) not in existing_analysis:
                    weather_analysis = WeatherAnalysis(
                        weather_station_id=row[0],
                        year=row[1],
                        avg_max_temp_celsius=row[2],
                        avg_min_temp_celsius=row[3],
                        accumulated_precipitation_cm=row[4]
                    )
                    new_analysis_records.append(weather_analysis)
            db.session.bulk_save_objects(new_analysis_records)
            db.session.commit()
            logger.info("Weather data analysis ingestion complete")
            num_analysis_records = len(new_analysis_records)
        
    except Exception as e:
        print(f"Error: {e}")

    return num_analysis_records



def ingest_data_main():
    """
    Main function to ingest weather and yield data, perform analysis, and store results in the database.

    This function consolidates weather and yield data from files, performs data analysis, 
    and pushes the raw and analyzed data into the database.

    It logs the number of records ingested and the total time taken for the process.
    """
    start_time = datetime.now()
    wx_df = wx_consolidation(WX_DATA)
    yld_df = yld_consolidation(YLD_DATA)
    print(wx_df, yld_df)
    wx_analysis_df = weather_analysis(wx_df)
    print(wx_analysis_df)
    num_wx_records, num_yld_records = push_raw_data(wx_df, yld_df)
    num_analysis_records = push_weather_analysis(wx_analysis_df)

    end_time = datetime.now()

    
    logger.info(f"Data ingestion completed in {(end_time - start_time).total_seconds()} seconds.")
    logger.info(f"Number of weather records ingested: {num_wx_records}")
    logger.info(f"Number of yield records ingested: {num_yld_records}")
    logger.info(f"Number of weather data analysis records ingested: {num_analysis_records}")
