import pandas as pd
import matplotlib.pyplot as plt


class ServicePlot:
        
    def plot(self, 
             report_name: str,
             plot_dataframe: pd.DataFrame) -> None:
        """Plot dataframe column against datetime index."""
        
        # Check if dataframe has only one column
        if len(plot_dataframe.columns) != 1:
            raise ValueError("Expected dataframe with exactly one column")
        
        # Plot aesthetics
        fig, ax = plt.subplots(figsize=(10,6))
        ax.set_facecolor('white')
        
        col = plot_dataframe.columns[0]
        cleaned_col_name = self._clean_column_name(col)
        
        ax.plot(plot_dataframe.index, plot_dataframe[col], label=cleaned_col_name)
        
        # Aesthetics
        title = f"{report_name}: {cleaned_col_name} Over Time"
        plt.title(title)
        plt.xlabel('Datetime')
        plt.ylabel(cleaned_col_name)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.6)
        ax.minorticks_on()
        ax.grid(which='minor', linestyle=':', linewidth=0.2, alpha=0.5)

        # Legend
        plt.legend(loc='upper left')
        
        # Formatting datetime for better aesthetics
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.gcf().autofmt_xdate()

        # Display plot and wait until it's closed
        plt.tight_layout()
        plt.show(block=True)

    def _clean_column_name(self, col: str) -> str:
        """Clean and format the column name for presentation."""
        return col.replace("_", " ").title()
