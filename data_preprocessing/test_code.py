# Read only region start
class UserMainCode(object):
    @classmethod
    def largestSubarray(cls, arr1, sizeof_arr):
        """
        input1: int

        input2 int[]
        Expected return type: int
        """
        # Read only region end

        # Write code here
        sum = 0
        maxsize = -1

        # Pick a starting point as i
        for i in range(0, sizeof_arr - 1):
            sum = -1 if (arr1[i] == 0) else 1
            # Consider all subarrays starting from i
            for j in range(i + 1, sizeof_arr):
                sum = sum + (-1) if (arr1[j] == 0) else sum + 1
                # If this is a 0 sum subarray, then
                # compare it with maximum size subarray
                # calculated so far

                if (sum == 0 and maxsize < j - i + 1):
                    maxsize = j - i + 1
                    startindex = i
        if (maxsize == -1):
            print("No such subarray");
        else:
            print(startindex, "to", startindex + maxsize - 1)

        return maxsize


# Driver program to test above functions
a = UserMainCode()
arr = [1, 0, 0, 1, 0, 1, 1]
size = len(arr)

a.largestSubarray(arr, size)
