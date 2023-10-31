from typing import Optional
from datetime import datetime, timedelta

from bmrs.services.service_plot import ServicePlot
from bmrs.services.service_bmrs_dataframe_analyser import \
                                ServiceBmrsDataframeAnalyser
from bmrs.services.service_bmrs_build_url import ServiceBmrsBuildUrl
from bmrs.services.service_bmrs_data_retriever import ServiceBmrsDataRetriever
from bmrs.converters.converter_dict_to_dataframe import ConverterDictToDataFrame


class ServiceRunMain:
    
    def __init__(self) -> None:
        self.service_plot = ServicePlot()
        self.service_bmrs_analyser = ServiceBmrsDataframeAnalyser()
        self.converter_dict_to_dataframe = ConverterDictToDataFrame()
        self.data_retriever = ServiceBmrsDataRetriever(url_builder=ServiceBmrsBuildUrl())
        

    def run(self, 
            reports : Optional[list[str]] = ['B1770','B1780']):
        """
        The ServiceRunMain class serves as an orchestrator to handle various services
        related to the BMRS (Balancing Mechanism Reporting Service) reports. It manages
        the entire lifecycle from data retrieval to plotting for the specified reports.

        Attributes:
        - service_plot: Service responsible for plotting the BMRS data.
        - service_bmrs_analyser: Service responsible for analyzing and processing BMRS data.
        - converter_dict_to_dataframe: Converter to transform dictionary BMRS data into a DataFrame.
        - data_retriever: Service responsible for fetching BMRS data.

        Methods:
        - run(reports: Optional[List[str]]): Orchestrates the workflow for the provided reports. 
        By default, it processes the 'B1770' and 'B1780' reports. It retrieves the report 
        data for a specified day (defaulted to one day prior to the current day), converts 
        the data into a DataFrame, calculates imbalances if required, and plots the results.

        Usage:
        service_runner = ServiceRunMain()
        service_runner.run(['B1770', 'B1780'])
        """
        
        previous_day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        for report_name in reports:
            
            report_dict = self.data_retriever.sync_retrieve_all_data(report_name=report_name,
                                                                     settlement_date=previous_day)
            
            report_dataframe = self.converter_dict_to_dataframe.convert(report_name=report_name,
                                                                        report_output=report_dict)
            
            self.service_bmrs_analyser.calculate_imbalances(report_name=report_name, 
                                                            report_ts_dataframe=report_dataframe)
            
            self.service_plot.plot(report_name=report_name,
                                   plot_dataframe=report_dataframe)
            
            