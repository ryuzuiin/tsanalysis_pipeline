from tsanalysis_pipeline.deep_learning.models.cnn import CNNTimeSeriesModel
from tsanalysis_pipeline.deep_learning.data_processing import TimeSeriesDataProcessor
from tsanalysis_pipeline.deep_learning.training import TimeSeriesTrainer
from tsanalysis_pipeline.deep_learning.evaluation import TimeSeriesEvaluator

def run_cnn_prediction(data, window_size=12, hidden_size=64, learning_rate=0.001, epochs=100):
    # Data processing
    data_processor = TimeSeriesDataProcessor(data, window_size=window_size)
    train_data, test_data, test_norm = data_processor.preprocess()

    # Model initialization
    model = CNNTimeSeriesModel(input_size=window_size, hidden_size=hidden_size)

    # Training
    trainer = TimeSeriesTrainer(model, train_data, learning_rate=learning_rate, epochs=epochs)
    trainer.train()

    # Evaluation
    evaluator = TimeSeriesEvaluator(model, data_processor, test_norm, window_size)
    predictions = evaluator.predict()

    true_values = data.iloc[-len(predictions):]
    mse, rmse, mape = evaluator.calculate_metrics(true_values, predictions)
    print(f"MSE: {mse:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%")

    evaluator.plot_results(true_values, predictions, trainer.get_train_losses())

    return predictions, mse, rmse, mape

# Usage
if __name__ == "__main__":
    # Assuming you have a DataFrame 'df' with your time series data
    import pandas as pd
    df = pd.read_csv('your_time_series_data.csv')  # Replace with your data source
    predictions, mse, rmse, mape = run_cnn_prediction(df)