from typing import Optional
from datetime import datetime, timedelta

from bmrs.services.service_plot import ServicePlot
from bmrs.services.service_bmrs_analyser import ServiceBmrsAnalyser
from bmrs.services.service_bmrs_build_url import ServiceBmrsBuildUrl
from bmrs.services.service_bmrs_data_retriever import ServiceBmrsDataRetriever
from bmrs.converters.converter_dict_to_dataframe import ConverterDictToDataFrame


class ServiceRunMain:
    
    def __init__(self) -> None:
        self.service_plot = ServicePlot()
        self.service_bmrs_analyser = ServiceBmrsAnalyser()
        self.converter_dict_to_dataframe = ConverterDictToDataFrame()
        self.data_retriever = ServiceBmrsDataRetriever(url_builder=ServiceBmrsBuildUrl())
        
    
    def run(self, 
            reports : Optional[list[str]] = ['B1770','B1780']):
        
        previous_day = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')

        for report_name in reports:
            
            report_dict = self.data_retriever.sync_retrieve_all_data(report_name=report_name,
                                                                     settlement_date=previous_day)
            
            report_dataframe = self.converter_dict_to_dataframe.convert(report_name=report_name,
                                                                        report_output=report_dict)
            
            updated_report_df = \
                self.service_bmrs_analyser.calculate_imbalances(report_name=report_name, 
                                                                report_ts_dataframe=report_dataframe)
            
            self.service_plot.plot(report_name=report_name,
                                   plot_dataframe=report_dataframe)
            
            