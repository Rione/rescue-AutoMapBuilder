import os
import sys

import numpy as np

sys.path.append(os.getcwd().replace('/src', ''))

from src.World import Building, Edge, Node, Road

MAP_WIDTH = 20
MAP_HEIGHT = 20


# 空白:-1
# 道:0
# 建物:1~

# 最初に配列にランダムに拠点を作る
# その時に別にIDとノード情報を保持するテーブルを作成
# 次に陣地をうばうように建物を広げていく
# その際にノード情報を更新していく(無い座標は追加、ある座標は削除)

class CreateMap:
    def __init__(self):
        self.map_array = np.full((MAP_WIDTH, MAP_HEIGHT), -1)
        self.building_list = {}
        self.road_list = {}

    def get_key(self, x: int, y: int):
        start = x + 1
        end = y + 1
        if start > end:
            return 10 ** len(str(start)) * end + start
        else:
            return 10 ** len(str(end)) * start + end

    def get_cross(self, map_array: np.ndarray, target_x: int, target_y: int):
        result = []
        if target_x - 1 >= 0:
            result.append(map_array[target_x - 1][target_y])

        if target_x + 1 < len(map_array):
            result.append(map_array[target_x + 1][target_y])

        if target_y - 1 >= 0:
            result.append(map_array[target_x][target_y - 1])

        if target_y + 1 < len(map_array):
            result.append(map_array[target_x][target_y + 1])

        return result

    def judge_neighbor(self, map_array: np.ndarray, distance: int, target_x: int, target_y: int):
        # 値が入っているかどうか確認
        # 指定場所に値が入っているか
        if not map_array[target_x][target_y] == -1:
            return False

        # xがはみ出していないか
        if target_x - distance >= 0:
            # 上下左右斜めで確認
            if not map_array[target_x - distance][target_y] == -1:
                return False
            if target_y - distance >= 0 and not map_array[target_x - distance][target_y - distance] == -1:
                return False
            if target_y + distance < len(map_array) and not map_array[target_x - distance][target_y + distance] == -1:
                return False

        if target_y - distance >= 0 and not map_array[target_x][target_y - distance] == -1:
            return False
        if target_y + distance < len(map_array) and not map_array[target_x][target_y + distance] == -1:
            return False

        if target_x + distance < len(map_array):
            if not map_array[target_x + distance][target_y] == -1:
                return False
            if target_y - distance >= 0 and not map_array[target_x + distance][target_y - distance] == -1:
                return False
            if target_y + distance < len(map_array) and not map_array[target_x + distance][target_y + distance] == -1:
                return False

        return True

    def can_put_building(self, map_array: np.ndarray, target_x: int, target_y: int):
        # 置けるならid,置けなければすでに入っているid、２つに挟まれている場合は0を返す
        # 指定場所に値が入っているか
        if not map_array[target_x][target_y] == -1:
            return map_array[target_x][target_y]

        building_count = 0
        tmp_id = 0

        # はじめに十字に見る
        if target_x - 1 >= 0:
            if not (map_array[target_x - 1][target_y] == -1 or map_array[target_x - 1][target_y] == 0 or
                    map_array[target_x - 1][target_y] == tmp_id):
                building_count += 1
                tmp_id = map_array[target_x - 1][target_y]

        if target_x + 1 < len(map_array):
            if not (map_array[target_x + 1][target_y] == -1 or map_array[target_x + 1][target_y] == 0 or
                    map_array[target_x + 1][target_y] == tmp_id):
                building_count += 1
                tmp_id = map_array[target_x + 1][target_y]

        if target_y - 1 >= 0:
            if not (map_array[target_x][target_y - 1] == -1 or map_array[target_x][target_y - 1] == 0 or
                    map_array[target_x][target_y - 1] == tmp_id):
                building_count += 1
                tmp_id = map_array[target_x][target_y - 1]

        if target_y + 1 < len(map_array):
            if not (map_array[target_x][target_y + 1] == -1 or map_array[target_x][target_y + 1] == 0 or
                    map_array[target_x][target_y + 1] == tmp_id):
                building_count += 1
                tmp_id = map_array[target_x][target_y + 1]

        if not building_count == 1:
            return 0

        # 斜め
        diagonal_count = 0
        if target_y - 1 >= 0:
            if target_x - 1 >= 0:
                if not (map_array[target_x - 1][target_y - 1] == -1 or map_array[target_x - 1][target_y - 1] == 0 or
                        map_array[target_x - 1][target_y - 1] == tmp_id):
                    diagonal_count += 1
            if target_x + 1 < len(map_array):
                if not (map_array[target_x + 1][target_y - 1] == -1 or map_array[target_x + 1][target_y - 1] == 0 or
                        map_array[target_x + 1][target_y - 1] == tmp_id):
                    diagonal_count += 1

        if target_y + 1 < len(map_array):
            if target_x - 1 >= 0:
                if not (map_array[target_x - 1][target_y + 1] == -1 or map_array[target_x - 1][target_y + 1] == 0 or
                        map_array[target_x - 1][target_y + 1] == tmp_id):
                    diagonal_count += 1
            if target_x + 1 < len(map_array):
                if not (map_array[target_x + 1][target_y + 1] == -1 or map_array[target_x + 1][target_y + 1] == 0 or
                        map_array[target_x + 1][target_y + 1] == tmp_id):
                    diagonal_count += 1

        if building_count == 0 and diagonal_count == 4:
            return 0
        if building_count == 0:
            return -1
        if diagonal_count == 0:
            return tmp_id
        return 0

    def judge_filled(self, array_map: np.ndarray):
        # 全て埋まったか
        for i in range(len(array_map)):
            if -1 in array_map[i]:
                return False
        return True

    ###################################################################################################

    def insert_edge_data(self, x1, y1, x2, y2):
        edge_id = self.get_key(self.get_key(x1, y1), self.get_key(x2, y2))
        node1 = Node.Node(self.get_key(x1, y1), x1, y1)
        node2 = Node.Node(self.get_key(x2, y2), x2, y2)
        return edge_id, Edge.Edge(edge_id, node1, node2)

    def get_edges(self, target_x: int, target_y: int):
        # 配列のindexから座標とkeyを生成、そこから更にエッジを生成する
        edge_keys = {}
        tmp = self.insert_edge_data(target_x, target_y, target_x + 1, target_y)
        edge_keys.setdefault(tmp[0], tmp[1])
        tmp = self.insert_edge_data(target_x, target_y, target_x, target_y + 1)
        edge_keys.setdefault(tmp[0], tmp[1])
        tmp = self.insert_edge_data(target_x, target_y + 1, target_x + 1, target_y + 1)
        edge_keys.setdefault(tmp[0], tmp[1])
        tmp = self.insert_edge_data(target_x + 1, target_y + 1, target_x + 1, target_y)
        edge_keys.setdefault(tmp[0], tmp[1])
        return edge_keys

    ###############################################################################################
    # road系
    def get_road_neighbor(self, map_array: np.ndarray, target_x: int, target_y: int):
        result = []
        if target_x - 1 >= 0 and map_array[target_x - 1][target_y] == 0:
            result.append(self.get_key(target_x - 1, target_y))

        if target_x + 1 < len(map_array) and map_array[target_x + 1][target_y] == 0:
            result.append(self.get_key(target_x + 1, target_y))

        if target_y - 1 >= 0 and map_array[target_x][target_y - 1] == 0:
            result.append(self.get_key(target_x, target_y - 1))

        if target_y + 1 < len(map_array) and map_array[target_x][target_y + 1] == 0:
            result.append(self.get_key(target_x, target_y + 1))

        return result

    ###############################################################################################

    def create_array_map(self, building_number: int):
        array_id = 1
        building_count = 0

        while building_count < building_number:
            # 配列にランダムに拠点を設定(ただし隣接は禁止)
            # x,yをランダムで選択
            target_x = np.random.randint(len(self.map_array))
            target_y = np.random.randint(len(self.map_array))

            # 隣接がないか確認
            if self.judge_neighbor(self.map_array, 1, target_x, target_y):
                self.map_array[target_x][target_y] = array_id
                array_id += 1
                building_count += 1

        # 占領開始
        while not self.judge_filled(self.map_array):
            for i in range(len(self.map_array)):
                for j in range(len(self.map_array)):
                    self.map_array[i][j] = self.can_put_building(self.map_array, i, j)

        # gml形式に落としこむ
        # building
        for i in range(len(self.map_array)):
            for j in range(len(self.map_array)):
                array_id = self.map_array[i][j]
                # roadの場合
                if array_id == 0:
                    road_id = self.get_key(i, j)
                    self.road_list.setdefault(road_id, Road.Road(road_id, self.get_road_neighbor(self.map_array, i, j)))

                # buildingの場合
                # idがすでにある場合
                if array_id in self.building_list:
                    self.building_list[array_id].update_nodes(self.get_edges(i, j))
                else:
                    self.building_list.setdefault(array_id, Building.Building(array_id))
                    self.building_list[array_id].update_nodes(self.get_edges(i, j))
        # print(self.road_list[512].neighbor_ids)


create = CreateMap()
create.create_array_map(25)

print(create.map_array)
