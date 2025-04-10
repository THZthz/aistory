import json


class IDGen:
    def __init__(self, filepath):
        self.occupied_ranges = []
        self.filepath = filepath

        # Load used id ranges from json file
        try:
            with open(filepath, 'r') as file:
                used_ids = json.load(file)
                occupied_ranges = used_ids['occupied_ranges']
                if not occupied_ranges is None:
                    self.occupied_ranges.extend(occupied_ranges)
        except FileNotFoundError:
            # Just ignore.
            pass

    def clear(self):
        self.occupied_ranges.clear()

    def save(self):
        """
        This function should be called when the program is closed to save all used ids.
        :return:
        """

        used_ids = json.dumps({'occupied_ranges': self.occupied_ranges}, indent=4)
        with open(self.filepath, "w") as outfile:
            outfile.write(used_ids)

    def get(self):
        if len(self.occupied_ranges) > 1:
            # We always allocate smallest id available

            assert self.occupied_ranges[0][1] < self.occupied_ranges[1][0]
            idx = self.occupied_ranges[0][1]
            self.occupied_ranges[0][1] += 1

            # Combine ranges
            if self.occupied_ranges[0][1] == self.occupied_ranges[1][0]:
                self.occupied_ranges[0][1] = self.occupied_ranges[1][1]
                self.occupied_ranges.pop(1)

            return idx
        elif len(self.occupied_ranges) == 1:
            self.occupied_ranges[0][1] += 1
            return self.occupied_ranges[0][1] - 1
        else:
            # Empty used ranges
            self.occupied_ranges.append([0, 1])
            return 0

    def put(self, idx):
        # Get lower bound
        left, right = 0, len(self.occupied_ranges)
        if right == 0: return # Empty ranges
        while left < right:
            mid = left + (right - left) // 2
            if self.occupied_ranges[mid][0] < idx:
                left = mid + 1
            else:
                right = mid
        left -= 1

        # Delete the id only if it exists
        if self.occupied_ranges[left][0] <= idx < self.occupied_ranges[left][1]:
            # Split the range
            self.occupied_ranges.insert(left + 1, [idx + 1, self.occupied_ranges[left][1]])
            self.occupied_ranges[left][1] = idx


    def __str__(self):
        return json.dumps(self.occupied_ranges, indent=4)
