import pandas as pd

def fill_frames(dataframe):
    # dataframe - a pandas dataframe containing the labelled columns x, y, frame
    # returns new dataframe without any missing frames
    filled_df = pd.DataFrame(columns = ['x', 'y', 'frame'])
    for i in range(1, dataframe.shape[0]):
        if (dataframe.frame[i] - dataframe.frame[i - 1]) > 1:
            for missing_frame in range(dataframe.frame[i-1] + 1, dataframe.frame[i]):
                filled_df.loc[missing_frame] = [dataframe.x[i-1], dataframe.y[i-1], missing_frame]
    dataframe.index = dataframe.frame
    dataframe.index.name = None
    dataframe = pd.concat([dataframe, filled_df]).sort_index()
    return(dataframe)

def calculate_velocity(dataframe):
    # dataframe - a dataframe object containing columns x, y, frame
    # returns the same dataframe object containing additional column 'velocity'
    from math import sqrt
    all_distances = []
    for i in range(0, dataframe.shape[0] - 1):
        all_distances.append(sqrt(((dataframe.x[i] - dataframe.x[i + 1])**2) + ((dataframe.y[i] - dataframe.y[i + 1])**2)))
    all_distances.insert(0, 0)
    dataframe['velocity'] = pd.Series(all_distances, index = dataframe.index)
    return(dataframe)

def calculate_rolling_velocity(dataframe, n = 10):
    # dataframe - a datafrane object containing columns x, y, frame, velocity
    # n - number of frames over which to average over
    # returns the same dataframe object containing additional column 'rolling_velocity'
    total_frames = dataframe.shape[0]
    mean_distance_per_n_frames = [None] * total_frames
    def mean(list):
        return(sum(list)/len(list))
    for i in range(n, total_frames - (n + 1)):
        mean_distance_per_n_frames[i] = mean(dataframe.velocity[i - n : i + n])
    dataframe['rolling_velocity'] = pd.Series(mean_distance_per_n_frames, index = dataframe.index)
    return(dataframe)

def filter_by_rolling_velocity(dataframe, cutoff):
    # dataframe - a pandas dataframe containing columns x, y, frame, velocity, rolling_velocity
    # cutoff - an integer
    # returns a new dataframe that satisfies the rolling velocity cutoff
    return(dataframe[dataframe.rolling_velocity > cutoff])

