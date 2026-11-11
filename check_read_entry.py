from broker.log import read_entry, scan

path = "logs/test.log"
starts = scan(path)[2]
for i in range(len(starts)):
    print(read_entry(path, starts, i))
print(read_entry(path,starts,len(starts)))
read_entry(path,starts,-1)
