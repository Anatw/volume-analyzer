import json
import os

import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt


folder_path = r'H:\Documents\Raven\raven sounds'
sound_rms_dict = {}
audio_name_list = []
sample_rate_list = []
mark_open = {}


def analysed_normalized_rms_dict(return_numpy_array=False):
    audio_data_dict = {}
    numpy_normalized_rms_dict = {}
    for audio_file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, audio_file)) and \
                audio_file.lower().endswith(".mp3"):
            audio_path = os.path.join(folder_path, audio_file)
            y, sr = librosa.load(audio_path, sr=None)
            S, phase = librosa.magphase(librosa.stft(y))
            # Plot the normalized RMS values:
            rms = librosa.feature.rms(S=S, hop_length=32)
            # Apply min-max normalization:
            normalized_rms = (rms - rms.min()) / (rms.max() - rms.min())
            numpy_normalized_rms_dict[audio_file] = normalized_rms
            audio_name_list.append(audio_file)
            sample_rate_list.append(sr)
            # Convert the numpy nd array into a list:
            normalized_rms_list = normalized_rms[0].tolist()
            sound_rms_dict[audio_path.split("\\")[-1]] = normalized_rms_list
    if return_numpy_array:
        return numpy_normalized_rms_dict
    for audio_name_index, track_name in enumerate(audio_name_list):
        audio_data_dict[track_name] = {
            "rms_values": sound_rms_dict[track_name],
            "sample_rate": sample_rate_list[audio_name_index],
        }
    return audio_data_dict


def exceeding_indexes_clusters():
    audio_data_dict = analysed_normalized_rms_dict()
    threshold = 0.2
    exceeded_indexes_dict = {}
    _exceeded_cluster_dict = {}  # Inner-use dictionary with start and end values for all the clusters in each audio track.
    exceeded_cluster_dict = {}
    # Create exceeded indexes dict:
    for audio_track, audio_data_value in audio_data_dict.items():
        exceeded_indexes = [
            index for index, value in enumerate(audio_data_value["rms_values"]) if
            value > threshold
        ]
        exceeded_indexes_dict[audio_track] = exceeded_indexes
        # Create exceeded clusters dict:
        _exceeded_cluster_dict[audio_track] = {}
        exceeded_cluster_dict[audio_track] = {}
        start = None
        distance_allowed_between_clusters = list(i for i in range(10, 101, 10))+[150, 300]
        num_clusters_added = []
        for distance in distance_allowed_between_clusters:
            cluster_index = 1
            _exceeded_cluster_dict[audio_track][distance] = {}
            for exceeded_list_index, exceeded_value in \
                    enumerate(exceeded_indexes_dict[audio_track]):
                if not start:
                    start = exceeded_value
                    _exceeded_cluster_dict[audio_track][distance][f"start{cluster_index}"] = start
                if len(exceeded_indexes_dict[audio_track]) > exceeded_list_index + 1 and \
                        (
                                exceeded_indexes_dict[audio_track][exceeded_list_index + 1] -
                                exceeded_indexes_dict[audio_track][exceeded_list_index]
                        ) < distance:
                    continue
                else:
                    _exceeded_cluster_dict[audio_track][distance][f"end{cluster_index}"] = exceeded_value
                    cluster_index += 1
                    start = None
            num_clusters_created = cluster_index - 1
            if num_clusters_created not in num_clusters_added:
                num_clusters_added.append(num_clusters_created)
                exceeded_cluster_dict[audio_track][distance] = {
                    "num_clusters": num_clusters_created,
                    "clusters": _exceeded_cluster_dict[audio_track][distance],
                    "num_values_in_cluster": len(audio_data_dict[audio_track]["rms_values"]),
                }
    return exceeded_cluster_dict


def print_exceeding_clusters():
    clusters = exceeding_indexes_clusters()
    for key, value in clusters.items():
        for inner_key, inner_value in value.items():
            print(key, inner_key, inner_value)
        print("\n")


def generate_clusters_for_servo_usage(print_clusters_details=False):
    _exceeding_indexes_clusters = exceeding_indexes_clusters()
    clusters_for_servo_usage = {}
    for track_name, clusters_dict in _exceeding_indexes_clusters.items():
        clusters_for_servo_usage[track_name] = {}
        for cluster_index, (distance, clusters) in enumerate(clusters_dict.items()):
            clusters_for_servo_usage[track_name][cluster_index] = []
            index = 1
            rms_ready_for_servo = []
            # For each track, in each distance dictionary, go over all the start and
            # stop values and create a new array with values according to which the
            # servo will operate.
            for index in range(1, (clusters["num_clusters"]+2)):
                if index == 1:  # If first range of the list
                    clusters_for_servo_usage[track_name][cluster_index] += \
                        [0] * (clusters["clusters"][f"start{index}"])
                elif index == (clusters["num_clusters"] + 1):  # If last range of the list
                    clusters_for_servo_usage[track_name][cluster_index] += \
                        [0] * (_exceeding_indexes_clusters[track_name][distance]
                                ['num_values_in_cluster'] -
                                clusters["clusters"][f"end{index-1}"])
                    break
                else:
                    clusters_for_servo_usage[track_name][cluster_index] += [0] * (clusters["clusters"][f"start{index}"] -
                                                  clusters["clusters"][f"end{index-1}"])
                plus = (clusters["clusters"][f"end{index}"] -
                        clusters["clusters"][f"start{index}"])
                clusters_for_servo_usage[track_name][cluster_index] += [1] * (plus if plus > 0 else 1)
        # clusters_for_servo_usage[track_name][cluster_index] = rms_ready_for_servo
    # Transfer the dict into a json format:
    for audio_name_index, track_name in enumerate(audio_name_list):
        clusters_for_servo_usage[track_name]["sample_rate"] = sample_rate_list[audio_name_index]
            # "rms_values": sound_rms_dict[track_name],
    print(json.dumps(clusters_for_servo_usage))
    if print_clusters_details:
        for track in clusters_for_servo_usage.items():
            print(f"track name: {track[0]}")
            for key, values_for_servo in track[1].items():
                print(f"cluster index: {key}")
                print(values_for_servo)


def generate_graphs(generate_rms=True, generate_power=False, generate_volume=False):
    num_arguments_passed = sum((generate_rms, generate_power, generate_volume))
    if not num_arguments_passed:
        print("Didn't generate any graphs, no parameters were selected")
        return
    rms_dict = analysed_normalized_rms_dict(return_numpy_array=True)
    for folder_path_index, audio_file in enumerate(os.listdir(folder_path)):
        if os.path.isfile(os.path.join(folder_path, audio_file)) and \
                audio_file.lower().endswith(".mp3"):
            audio_path = os.path.join(folder_path, audio_file)
            fig, ax = plt.subplots(nrows=num_arguments_passed, sharex=True)
            rms = rms_dict[audio_file]
            graph_index = 0
            times = librosa.times_like(rms)
            enumerate_of_rms_values = np.arange(rms.shape[1])
            if num_arguments_passed > 1:
                if generate_rms:
                    ax[graph_index].semilogy(times, rms[0], label='RMS Energy')
                    ax[graph_index].semilogy(enumerate_of_rms_values, rms[0], label='RMS Energy')
                    ax[graph_index].set_xticks(enumerate_of_rms_values[::10])
                    ax[graph_index].set_xticklabels(enumerate_of_rms_values[::10])
                    graph_index += 1
                if generate_power:
                    y, sr = librosa.load(audio_path, sr=None)
                    S, phase = librosa.magphase(librosa.stft(y))
                    librosa.display.specshow(librosa.amplitude_to_db(S, ref=np.max), y_axis='log', x_axis='time', ax=ax[graph_index])
                    ax[graph_index].set(title='log Power spectrogram')
                    librosa.magphase(librosa.stft(y, window=np.ones, center=False))[0]
                    graph_index += 1
                if generate_volume:
                    volume = librosa.amplitude_to_db(rms, ref=np.max)
                    ax[graph_index].plot(times, volume[0], label='Volume')
                    ax[graph_index].set_xlim([times.min(), times.max()])
                    ax[graph_index].set_ylabel('Volume')
                    ax[graph_index].legend()
            else:
                if not generate_rms:
                    print("Can only generate a single graph with RMS values, and this is not what was requested")
                    return
                ax.semilogy(enumerate_of_rms_values, rms[0], label='RMS Energy')
                ax.set_xticks(enumerate_of_rms_values[::10])
                ax.set_xticklabels(enumerate_of_rms_values[::10])
            plt.savefig(audio_path.split("\\")[-1].replace("mp3", "png"))
            # plt.figure(figsize=(12, 4), num=audio_file)
            # librosa.display.waveshow(y, sr=sr)
            plt.title(audio_file)

            plt.show()


def main():
    analysed_normalized_rms_dict()
    generate_graphs(generate_power=True, generate_volume=True)
    exceeding_indexes_clusters()
    print_exceeding_clusters()
    generate_clusters_for_servo_usage()


if __name__ == '__main__':
    main()

