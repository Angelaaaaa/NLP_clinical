class DataPointConfig:
    def __init__(self, dp_name, window_size,select_numerical,present_row_limit,ignore_wordlist):
        # keyword
        self.self_dp_name = dp_name
        # window size
        self.self_window_size = window_size
        # if only select numerical number
        self.self_select_numerical = select_numerical
        # eg. top 50
        self.self_present_row_limit = present_row_limit
        # list of words that doesnt need to be selected
        self.self_ignore_wordlist = ignore_wordlist