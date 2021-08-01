import matplotlib.pyplot as plt

class Plotter():
    def plot(self, data):
        plt.bar(*zip(*data.items()))
        # *zip(*dict.items()) consists of two tuples, one containing the unpacked keys of the dictionary
        # and one containing the corresponding unpacked values
        plt.xticks(rotation = 90) # Rotate horizontal axis labels by 90 degrees
        plt.tick_params(labelsize = 7) # not good
        plt.show()

## Testing
def main():
    Plotter().plot("vgc")
    
if(__name__  == "__main__"): main()
