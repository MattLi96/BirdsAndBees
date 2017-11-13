import os

output_path = "../output/"
public_data = "../data/overview/"
public_out_path = "../public/data/"

no_game = False  # Only use the no game no life wiki. Intended for testing
no_game_name = "nogamenolife"
time_series = True  # If true do time series. Otherwise process file

generate_data = True  # True to generate data folder items

performance_mode = False
large_wikis = ["fullhouse", "gameofthrones", "marvel"]

cpu = os.cpu_count() if os.cpu_count() else 4
threads = cpu  # Adjust depending on how CPU/RAM intensive task is
