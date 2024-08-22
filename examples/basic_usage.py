from tsanalysis_pipeline import CSVColumnExtractor, ModelingTimeSeriesAnalyzer


if __name__ == "__main__":
    extractor = CSVColumnExtractor('data', {'file1.csv': ['column1', 'column2']}, 'timestamp')
    data = extractor.extract_columns()

    analyzer = ModelingTimeSeriesAnalyzer(data, 'timestamp', 'value')
    analyzer.run_modeling_analysis()