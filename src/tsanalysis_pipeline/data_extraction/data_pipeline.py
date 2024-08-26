import os
import zipfile
import pandas as pd
import logging
from typing import List, Optional, Dict

logging.basicConfig(
  level = logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 设置日志格式
  datefmt='%Y-%m-%d %H:%M:%S',  # 设置时间格式
  filename='data_pipeline.log',  # 指定日志文件的名称和路径（如果你希望将日志记录到文件）
  filemode='a'  # 追加模式，日志会被追加到文件末尾，使用'w'则是覆盖模式
)

logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, base_path: str, zip_file: str, unzip_dir: str) -> None:
        '''
        Initialize the class with the base path and target directories.

        Parameters:
        base_path (str): The base path, usually a Google Drive path
        zip_file (str): The name of the zip file
        unzip_dir (str): The directory where the unzipped files will be stored

        Returns:
        None
        '''
        self.base_path: str = base_path
        self.zip_path: str = os.path.join(base_path, zip_file)
        self.unzip_path: str = os.path.join(base_path, unzip_dir)
        self.csv_files: List[str] = []

    def unzip_files(self) -> None:
        '''
        Unzip files in the specified directory and extract only CSV files.

        Returns:
        None
        '''
        if not os.path.exists(self.unzip_path):
            os.makedirs(self.unzip_path)
            logger.info(f"Created directory: {self.unzip_path}")

        logger.debug(f"Checking for zip file: {self.zip_path}")

        if not os.path.exists(self.zip_path):
            logger.error(f"The file {self.zip_path} does not exist.")
            return

        logger.debug(f"Files in base directory: {os.listdir(self.base_path)}")

        with zipfile.ZipFile(self.zip_path, 'r') as z:
            for file_info in z.infolist():
                if file_info.filename.endswith('.csv'):
                    file_info.filename = os.path.basename(file_info.filename)
                    z.extract(file_info, self.unzip_path)
                    logger.info(f"Extracted {file_info.filename} to {self.unzip_path}")

    def list_csv_files(self) -> List[str]:
        '''
        List all CSV files in the unzipped directory.

        Returns:
        List[str]: A list of paths to all CSV files
        '''
        for root, _, files in os.walk(self.unzip_path):
            for file in files:
                if file.endswith('.csv'):
                    self.csv_files.append(os.path.join(root, file))
        logger.info(f"CSV files found: {self.csv_files}")
        return self.csv_files

    def process(self) -> List[str]:
        '''
        Process the data pipeline: unzip and list CSV files.

        Returns:
        List[str]: A list of processed CSV files
        '''
        self.unzip_files()
        return self.list_csv_files()

    def merge_all_csv_files(self, output_filename: str) -> Optional[str]:
        '''
        Merge all CSV files into a single DataFrame and save to the output file.

        Parameters:
        output_filename (str): The name of the merged output CSV file

        Returns:
        Optional[str]: The path to the output file if successful, None if an error occurs
        '''
        bad_files: List[str] = []
        bad_lines: Dict[str, List[int]] = {}

        df: pd.DataFrame = pd.DataFrame()
        for file in self.csv_files:
            try:
                tmp_df: pd.DataFrame = pd.read_csv(file, encoding='shift-jis', encoding_errors='replace', on_bad_lines='warn', engine='python')
                if tmp_df.empty:
                    logger.warning(f"File {file} is empty.")
                    continue
                logger.info(f"Read {file}: {tmp_df.shape[0]} rows")
                df = pd.concat([df, tmp_df], ignore_index=True)
            except (pd.errors.ParserError, ValueError, pd.errors.EmptyDataError) as e:
                logger.error(f"Error reading file: {file}")
                logger.error(e)
                bad_files.append(file)

                line_info = str(e).split('\n')[0]
                line_number: Optional[int] = None
                try:
                    line_number = int(line_info.split(':')[1].split(' ')[-1])
                except (IndexError, ValueError):
                    pass

                if line_number is not None:
                    if file in bad_lines:
                        bad_lines[file].append(line_number)
                    else:
                        bad_lines[file] = [line_number]

        if bad_files:
            logger.error(f"The following files had errors: {bad_files}")
            for bad_file in bad_files:
                if bad_file in bad_lines:
                    logger.error(f"Line numbers with errors in {bad_file}: {bad_lines[bad_file]}")
            return None
        else:
            logger.info("No errors found.")

        output_path: str = os.path.join(self.unzip_path, output_filename)
        df.to_csv(output_path, index=False)
        logger.info(f"Merged CSV saved to {output_path}")
        return output_path
