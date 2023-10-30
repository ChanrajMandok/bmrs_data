
 
# **Smartest BMRS** - Trading Data Retrieval Task 

## Setup Smartest_Bmrs in VSC

|Action|Command
| :-| :-
|Create a virtual environment| python -m venv .venv
|Install relevant libraries | pip install -r requirements.txt|
|Create json launch file| Open and Paste contents of launch_items.txt (ensure commas are correct) and Save|
|Run|Select Dropdown Menu and Select Run main|

## Enviroment Variables

|Environment variable|value|
| :-| :-
|MAX_TRIES | 3
|TIMEOUT | 10
|VERSION | V1
|MAX_CONCURRENCT_TASKS| 24
|B1770_COLUMN|  <span style="color:green">imbalancePriceAmountGBP
|B1780_COLUMN|  <span style="color:green">imbalanceQuantityMAW
|API_SCRIPTING_KEY | <span style="color:red">Insert Scripting key Generated</span>
|HOST| https://api.bmreports.com/BMRS/
|URL_END_STR| {SettlementDate}&Period={Period}&ServiceType={ServiceType}

