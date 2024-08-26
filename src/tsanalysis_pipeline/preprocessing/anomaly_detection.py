class AnomalyDetector:
    def __init__(self, directory, year_col='Year'):
        self.directory = directory
        self.year_col = year_col

    @staticmethod
    def identify_column_format(series):
        if series.isnull().all():
            return 'Empty'
        if pd.api.types.is_numeric_dtype(series):
            if series.dtype == 'int64':
                return 'Integer'
            else:
                return 'Float'
        try:
            pd.to_datetime(series, errors='coerce')
            return 'Date'
        except:
            pass
        if series.dtype == 'object':
            return 'Object'
        return 'Unknown'

    def standardize_numeric(self, series):
        return pd.to_numeric(series, errors='coerce')

    def standardize_date(self, series):
        return pd.to_datetime(series, errors='coerce')

    def standardize_object(self, series):
        return pd.to_numeric(series, errors='coerce')

    def standardize_columns(self, series):
        column_format = self.identify_column_format(series)
        if column_format == 'Empty':
            return series
        elif column_format in ['Integer', 'Float']:
            return self.standardize_numeric(series)
        elif column_format == 'Date':
            return self.standardize_date(series)
        elif column_format == 'Object':
            return self.standardize_object(series)
        else:
            return series

    def standardize_dataframe(self, df):
        for column in df.columns:
            df[column] = self.standardize_columns(df[column])
        return df

    @staticmethod
    def count_garbled_characters(series):
      garbled_pattern = re.compile(r'[^\x00-\x7F]+')
      garbled_count = series.apply(lambda x : len(garbled_pattern.findall(str(x))) if pd.notnull(x) else 0).sum()
      return garbled_count

    def detect_anomalies(self, df):
        anomalies = {}
        for col in df.columns:
            if col == self.year_col:
                continue
            total_count = len(df[col])
            null_count = df[col].isnull().sum()
            zero_count = (df[col] == 0).sum()
            asterisk_count = (df[col] == '*').sum()
            garbled_count = self.count_garbled_characters(df[col])
            unique_count = df[col].nunique()
            anomalies[col] = {
                'total': total_count,
                'null': null_count,
                'zero': zero_count,
                'asterisk': asterisk_count,
                'garbled': garbled_count,
                'unique': unique_count
            }
        return anomalies

    def read_csv_with_multiple_encodings(self, file):
        encodings = ['shift_jis', 'utf-8', 'euc-jp', 'cp932']
        for encoding in encodings:
            try:
                df = pd.read_csv(file, encoding=encoding)
                return df, encoding
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"Failed to decode {file} with any of the tried encodings.")

    def process_file(self, file):
        print(f"Starting to process file: {file}")
        result = {}
        all_columns = set()
        try:
            df, encoding = self.read_csv_with_multiple_encodings(file)
            if df.empty:
                print(f'Warning: No data found in {file}. Skipping.')
                return pd.DataFrame()

            print(f"Processing file {file} with encoding {encoding}")
            all_columns.update(df.columns)
            df = self.standardize_dataframe(df)

            if self.year_col in df.columns:
                years = df[self.year_col].unique()
                for year in years:
                    year_data = df[df[self.year_col] == year]
                    anomalies = self.detect_anomalies(year_data)
                    if year not in result:
                        result[year] = {}
                    for col, counts in anomalies.items():
                        if col not in result[year]:
                            result[year][col] = counts
                        else:
                            for count_type, count in counts.items():
                                result[year][col][count_type] += count
            else:
                print(f'Warning: No year column found in {file}. Using filename as year.')
                year = os.path.splitext(os.path.basename(file))[0]
                anomalies = self.detect_anomalies(df)
                result[year] = anomalies

        except pd.errors.EmptyDataError:
            print(f'Warning: File {file} is empty or has no parseable data. Skipping.')
        except Exception as e:
            print(f'Error processing file {file}: {e}. Skipping.')

        if not result:
            print("No valid data found in the file.")
            return pd.DataFrame()

        # Create multi-index
        columns = pd.MultiIndex.from_product([result.keys(), ['null', 'zero', 'asterisk']])
        all_columns.discard(self.year_col)
        result_df = pd.DataFrame(index=list(all_columns), columns=columns)

        for year in result:
            for col in result[year]:
                for anomaly_type in result[year][col]:
                    result_df.loc[col, (year, anomaly_type)] = result[year][col][anomaly_type]

        print("Result DataFrame:\n", result_df)  # Diagnostic print to check the DataFrame structure
        return result_df

   #Import the whole directory, need to be modified, not work so well, almost the same code as process_file.
    def process_files(self):
        print("Starting to process files...")
        result = {}
        all_columns = set()
        for file in glob.glob(os.path.join(self.directory, '*.csv')):
            try:
                df, encoding = self.read_csv_with_multiple_encodings(file)
                if df.empty:
                    print(f'Warning: No data found in {file}. Skipping.')
                    continue

                print(f"Processing file {file} with encoding {encoding}")
                all_columns.update(df.columns)
                df = self.standardize_dataframe(df)

                if self.year_col in df.columns:
                    years = df[self.year_col].unique()
                    for year in years:
                        year_data = df[df[self.year_col] == year]
                        anomalies = self.detect_anomalies(year_data)
                        if year not in result:
                            result[year] = {}
                        for col, counts in anomalies.items():
                            if col not in result[year]:
                                result[year][col] = counts
                            else:
                                for count_type, count in counts.items():
                                    result[year][col][count_type] += count
                else:
                    print(f'Warning: No year column found in {file}. Using filename as year.')
                    year = os.path.splitext(os.path.basename(file))[0]
                    anomalies = self.detect_anomalies(df)
                    result[year] = anomalies

            except pd.errors.EmptyDataError:
                print(f'Warning: File {file} is empty or has no parseable data. Skipping.')
            except Exception as e:
                print(f'Error processing file {file}: {e}. Skipping.')

        if not result:
            print("No valid data found in any file.")
            return pd.DataFrame()

        # Create multi-index
        columns = pd.MultiIndex.from_product([result.keys(), ['null', 'zero', 'asterisk']])
        all_columns.discard(self.year_col)
        result_df = pd.DataFrame(index=list(all_columns), columns=columns)

        for year in result:
            for col in result[year]:
                for anomaly_type in result[year][col]:
                    result_df.loc[col, (year, anomaly_type)] = result[year][col][anomaly_type]

        print("Result DataFrame:\n", result_df)  # Diagnostic print to check the DataFrame structure
        return result_df

   # the gate of whole module!!!
    def generate_report(self, input_file=None):
        if input_file:
            print(f"Processing single input file: {input_file}")
            result_df = self.process_file(input_file)
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f'anomaly_report for {base_name}.csv'
            result_df.to_csv(output_file, encoding='utf-8-sig')
            print(f'Anomalies report generated successfully! Saved to {output_file}')
        else:
            print("Processing all files in the directory...")
            result_df = self.process_files()
            if not result_df.empty:
              for file in  glob.glob(os.path.join(self.directory, '*.csv')):
                base_name = os.path.splitext(os.path.basename(file))[0]
                print(f"Processing file: {base_name}"
                output_file = f'anomaly_report for {base_name} .csv'
                result_df.to_csv(output_file, encoding='utf-8-sig')
                print(f'Anomalies report generated successfully! Saved to {output_file}')
            else:
                print("No report generated due to lack of valid data.")

