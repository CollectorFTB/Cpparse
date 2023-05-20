from statements import HFile

def main():
    with open('examples/yuzu/constants.h', 'rb') as f:
        data = f.read()
    
    parsed_h_file = HFile.parse(data)
    print(parsed_h_file)

if __name__ == '__main__':
    main()