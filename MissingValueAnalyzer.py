class MissingValueAnalyzer:
    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        self.train_df = train_df
        self.test_df = test_df
        self.train_missing_summary = None
        self.test_missing_summary = None
        
    def generate_missing_summary(self, df, df_name='DataFrame'):
        missing_summary = df.isnull().sum()
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        missing_df = pd.DataFrame({
            "Missing Values": missing_summary,
            "Missing Percentage (%)": missing_percentage
        })
        missing_df = missing_df[missing_df['Missing Values'] > 0].sort_values(by= 'Missing Percentage (%)', ascending=False)
    
        print(f"\n{df_name} - Missing Values Summary:")
        print(tabulate(missing_df, headers='keys', tablefmt='grid'))
        
        return missing_df
    
    def generate_descriptive_statistics(self, df, df_name="DataFrame"):
        describe_df = df.describe(include='all')
        
        print(f"\n{df_name} - Descriptive Statistics:")
        print(tabulate(describe_df, headers='keys', tablefmt='grid'))
        
    def plot_missing_values(self):
        if self.train_missing_summary is None or self.test_missing_summary is None:
            print("Please run analyze_missing_values first to generate summaries.")
            return
        
        self.plot_stacked_bar(self.train_df, 'train_df')
        
        self.plot_stacked_bar(self.test_df, 'test_df')
        
        
        
        
    def plot_stacked_bar(self, df, df_name):
        missing_df = pd.DataFrame({
            'Feature': df.columns,
            'Missing Count': df.isnull().sum(),
            'Missing Percentage': df.isnull().sum() / len(df) * 100,
            'Available count': df.notnull().sum(),
            'Available Percentage': df.notnull().sum() / len(df) * 100
        }).sort_values(by='Missing Percentage', ascending=False)
        
        plt.figure(figsize=(10, 18))
        missing_df.set_index('Feature')[['Missing Percentage', 'Available Percentage']].plot(
            kind='barh', stacked=True, color=['#e41a1c', '#4daf4a'], figsize=(10, 18)
        )
        
        plt.title(f'Missing values over the {df_name}', fontsize=16)
        plt.xlabel('Percentage')
        plt.ylabel('Feature')
        plt.legend(['Missing', 'Available'], loc='upper right')
        plt.tight_layout()
        plt.show()
        
        
    def analyze_missing_values(self):
        self.train_missing_summary = self.generate_missing_summary(self.train_df, "train_df")
        self.test_missing_summary = self.generate_missing_summary(self.test_df, "test_df")
        
#         self.generate_descriptive_statistics(self.train_df, "train_df")
#         self.generate_descriptive_statistics(self.test_df, "test_df")
        
        self.plot_missing_values()
