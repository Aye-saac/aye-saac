
import sys
import cv2
import keras_ocr
import argparse
import math
import matplotlib.pyplot as plt
from pprint import pprint
from spellchecker import SpellChecker


def calc_closest_neighbour(data, key, point, dim):
    min_d = sys.maxsize
    closest_n = None
    text = ''
    for n_key in data:
        if n_key != key:
            tmp_dist = math.sqrt(
                (point[0] - data[n_key]['pos'][dim][0]) ** 2 + (point[1] - data[n_key]['pos'][dim][1]) ** 2)
            if tmp_dist <= data[key]['max_dist'][dim] and tmp_dist < min_d:
                min_d = tmp_dist
                closest_n = n_key
                text = data[n_key]['text']

    return {'d': min_d, 'key': closest_n, 'text': text}


def calc_dist_btw_boxes(data):
    for key in data:
        data[key]['closest'] = {'L': calc_closest_neighbour(data, key, data[key]['pos']['L'], 'R'),
                                'R': calc_closest_neighbour(data, key, data[key]['pos']['R'], 'L'),
                                'U': calc_closest_neighbour(data, key, data[key]['pos']['U'], 'D'),
                                'D': calc_closest_neighbour(data, key, data[key]['pos']['D'], 'U')
                                }
    return data


def get_idx_from_key(all, key):
    for i, x in enumerate(all):
        if key == x[0]:
            return i
    return -1


def lines_to_phrases(link, all):
    change = False
    idx = 0
    while idx < len(link):
        i = get_idx_from_key(all, link[idx][0])
        ii = get_idx_from_key(all, link[idx][1])
        if i != -1 and ii != -1:
            change = True
            all[i] += all[ii]
            del all[ii]
            del link[idx]
        idx += 1
    return all, change


def lines_only_to_all_text(lines, all):
    # remove all duplicate
    for l in lines:
        for ll in l:
            if ll in all:
                all.remove(ll)
    # add the single word
    for x in all:
        lines.append([x])
    # sort by y-axis top to bottom
    lines.sort(key=lambda r: int(r[0]))
    return lines


def lines_creator(link):
    """
    B...A + C...B => C...B...A
    A...B + B...C => A...B...C
    """
    change = False
    i = 0
    while i < len(link):
        for ii in range(len(link)):
            if i != ii:
                if link[i][-1] == link[ii][0]:
                    change = True
                    for x in link[ii][1:]:
                        link[i].append(x)
                    del link[ii]
                    break
                elif link[i][0] == link[ii][-1]:
                    change = True
                    for x in link[i][1:]:
                        link[ii].append(x)
                    del link[i]
                    break
        i += 1
    return link, change


def link_by_directions(graph, direction, opposite_direction):
    link = []

    for a, b in graph[direction]:
        for c, d in graph[opposite_direction]:
            if (a == c or a == d) and (b == c or b == d):
                link.append([a, b])

    return link


def words_to_lines(nodes, links):
    lines = link_by_directions(links, 'R', 'L')

    change = True
    while change:
        lines, change = lines_creator(lines)

    lines = lines_only_to_all_text(lines, nodes)

    return lines


def search_links_btw_word(data):
    directions = ['U', 'D', 'L', 'R']
    link = {'U': [], 'D': [], 'L': [], 'R': []}
    for key in data:
        for d in directions:
            if data[key]['closest'][d]['key'] is not None:
                link[d].append([key, data[key]['closest'][d]['key']])
    return link


def init(texts):
    data = {}
    for idx, (text, bbox) in enumerate(texts):
        if not len(text):
            continue
        data[str(idx)] = {'text': text,
                          'bbox': bbox,
                          'max_dist': {'R': (((bbox[1][0] - bbox[0][0]) / len(text)) + (
                                      (bbox[2][0] - bbox[3][0]) / len(text))) / 2,
                                       'L': (((bbox[1][0] - bbox[0][0]) / len(text)) + (
                                                   (bbox[2][0] - bbox[3][0]) / len(text))) / 2,
                                       'D': ((bbox[3][1] - bbox[0][1]) + (bbox[2][1] - bbox[1][1])) / 2,
                                       'U': ((bbox[3][1] - bbox[0][1]) + (bbox[2][1] - bbox[1][1])) / 2
                                       },
                          'pos': {'L': [(bbox[3][0] + bbox[0][0]) / 2, (bbox[3][1] + bbox[0][1]) / 2],
                                  'R': [(bbox[2][0] + bbox[1][0]) / 2, (bbox[2][1] + bbox[1][1]) / 2],
                                  'U': [(bbox[1][0] + bbox[0][0]) / 2, (bbox[1][1] + bbox[0][1]) / 2],
                                  'D': [(bbox[2][0] + bbox[3][0]) / 2, (bbox[2][1] + bbox[3][1]) / 2]},
                          'key': str(idx)
                          }

    data = calc_dist_btw_boxes(data)
    return data


def bb_to_text(predictions):
    data = init(predictions)
    nodes = [data[x]['key'] for x in data]
    links = search_links_btw_word(data)

    lines = words_to_lines(nodes, links)
    lines_link = link_by_directions(links, 'D', 'U')

    change = True
    while change:
        lines, change = lines_to_phrases(lines_link, lines)

    spell = SpellChecker(distance=1)
    text = []
    for l in lines:
        phrase = []
        for ll in l:
            phrase.append(spell.correction(data[ll]['text']))
        text.append(phrase)
    return text
