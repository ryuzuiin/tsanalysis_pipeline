class Dailyloogger:
  def __init__(self, working_path: str, log_folder_name: str = 'logs', log_filename: str = None):
    self.working_path = working_path
    self.log_folder_name = log_folder_name

    # daily logger path
    self.log_folder_path = os.path.join(self.working_path, self.log_folder_name)

    # Create the log folder if it doesn't exist
    if not os.path.exists(self.log_folder_path):
      os.makedirs(self.log_folder_path)

    # dynamic logger name
    if log_filename is None:
      current_date = datetime.now().strftime('%Y%m%d')
      self.log_filename = f'log_{current_date}.log'
    else:
      self.log_filename = log_filename

    # log file path
    self.log_file_path = os.path.join(self.log_folder_path, self.log_filename)

    # check if log file path is correct
    print(f'Log file path: {self.log_file_path}')

    logging.basicConfig(
        filename=self.log_file_path,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info(f"Log file created: {self.log_file_path}")
    logging.info(f"Logging started for {self.log_filename}")
    logging.info(f"Working path: {self.working_path}")
    logging.info(f"Log folder path: {self.log_folder_path}")

  def get_logger(self):
    return logging.getLogger()

  def log_info(self, message):
    logging.info(message)

  def log_warning(self, message):
    logging.warning(message)

  def log_error(self, message):
    logging.error(message)

  def log_debug(self, message):
    logging.debug(message)

  def log_experiment(self, experiment_name: str, params: dict, metrics: dict, plot=None):
    logging.info(f"Experiment: {experiment_name}")
    logging.info(f"Parameters: {params}")
    logging.info(f"Metrics: {metrics}")

    if plot is not None:
      plot_filename = self.save_plot(plot, experiment_name)
      logging.info(f'plot saved: {plot_filename}')

  def log_feature_engineering(self, feature_class_name: str, params: dict):
    logging.info(f"Feature Engineering: {feature_class_name}")
    logging.info(f"Parameters: {params}")


  def save_plot(self, plot: plt.Figure, filename: str = None, dynamic_name: bool = False) -> None:

    plot_folder_path = os.path.join(self.working_path, 'plots')
    if not os.path.exists(plot_folder_path):
      os.makedirs(plot_folder_path)

    if dynamic_name:
      current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
      plot_filename = f'plot_{current_time}.png'
    else:
      plot_filename = filename

    plot_file_path = os.path.join(plot_folder_path, plot_filename)

    plot.tight_layout()
    plot.savefig(plot_file_path)
    logging.info(f'Plot saved: {plot_file_path}')
    return plot_file_path

  def save_csv(self, df: pd.DataFrame, filename: str, encoding: str = 'utf-8-sig') -> str:

    data_folder_path = os.path.join(self.working_path, 'data')
    if not os.path.exists(data_folder_path):
      os.makedirs(data_folder_path)

    csv_file_path = os.path.join(data_folder_path, filename)
    df.to_csv(csv_file_path, index=False, encoding=encoding)
    logging.info(f'CSV file saved: {csv_file_path}')
    return csv_file_path

  def save_json(self, data: dict, filename: str) -> None:

    json_file_path = os.path.join(self.working_path, 'results', filename)

    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    with open(json_file_path, 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=4)
    self.log_info(f'JSON file saved: {json_file_path}')

  def get_log_file_path(self):
    return self.log_file_path
