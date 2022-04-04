# Prepare LDBC SNB 10 TB data
## Table of Contents
* [Direct download](#Direct-download-(not-recommended))
* [Download one partition](#Download-one-partition-of-the-data)
   * [Pre-requisites](#Pre-requisites)
   * [Download data](#Download-data)
   * [Decompress data](#Decompress-data)
* [Load, run and update](#Load,-Run-and-Update)
* [About queries](#About-queries)

&nbsp;
## Direct download (not recommended)
The location of data
- 1TB LDBC SNB data: 
   - gs://ldbc_snb_1t/sf1k/
- 10TB LDBC SNB data
   - gs://ldbc_snb_10t_v2//composite-projected-fk/
- 30TB LDBC SNB data
   - gs://ldbc_snb_30t_v2/composite-projected-fk/

You can use `gsutil ls` to explore the two folder. This requires installation of [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
```sh
gsutil ls gs://ldbc_snb_10t/v1/results/sf10000-compressed/runs/20210713_203448/social_network/csv/bi/composite-projected-fk/
```
The ending `/` must be included. You will see four folders
- initial_snapshot
- inserts
- inserts_split
- deletes

The `inserts_split` stores the same data as `inserts` but csv files are split into smaller CSV files. The command to download the whole dataset is
```sh
gsutil -m cp -r  gs://ldbc_snb_10t/v1/results/sf10000-compressed/runs/20210713_203448/social_network/csv/bi/composite-projected-fk/ .  
```
option `-m` means using multiple threads. When using multiple machines, I recommend to only donwload one part for each machine. The procedures is in the next section.

## Download one partition of the data
This is the guide for downloading one partition of the data for one of the machine. You need to repeat the downloading and decompressing procedures for all the machines.

### Pre-requisites
The scrit also requires python installation and `google-cloud-storage` package. Decompressing data requires `gzip` and `GNU parallel`. On CentOS, the command is
```sh
sudo yum install -y  python3-pip perl bzip2 gzip wget lynx
# install google-cloud-storage package
pip3 install google-cloud-storage
# install GNU parallel
(wget -O - pi.dk/3 || lynx -source pi.dk/3 || curl pi.dk/3/ || \
   fetch -o - http://pi.dk/3 ) > install.sh
sh install.sh
```

&nbsp;
### Download data
Use the script `download_one_partition.py` to download one partition of the data. The python script requires a GCP service key in JSON format. The data is public and open to all users, so you can use the service key from any Google account. The tutorial for creating the service key can be found on [GCP document](https://cloud.google.com/docs/authentication/getting-started).

The usage of the script is `python3 download_one_partition.py [data size] [node index] [number of nodes] -k [service-key file] -t [number of threads]`. For a cluster of 4 nodes, you need to run the command on all of the 4 nodes and use the nodex index 0,1,2,3 for each machine. I also prefer to run in background using nohup.

Currently, the delete operation is not distributed, and the same copy of delete data need be kept on all the nodes.
```sh
# on node m1
nohup python3 -u download_one_partition.py 10k 0 4  > foo.out 2>&1 < /dev/null &
```
Available data size is `1k`, `10k` and `30k`, corresponding to about 1T, 10T and 40T data. The GCS bucket address is hard coded in the code. The data is downloaded to `./sf1k`, `./sf10k` and `./sf30k`, respectively. 

### Decompress data
Decompress the data on each node in parallel.
```sh
cat << EOF > uncompress.sh
cd sf10k
mv inserts_split inserts 
find . -name *.gz  -print0 | parallel -q0 gunzip 
echo 'done uncompress'
EOF
nohup sh uncompress.sh  > foo2.out 2>&1 < /dev/null &
```

&nbsp;
### Download for all the machines
The above commands only download the data for one of the machine. You need to repeat the procedure in downloading and decompressing for all the machines.
If you have pre-requisite packages setup on all the machines, you can also use the script `download_all.py` to download and decompress data for machines with contiguous IP address. The script connect to other machines and run the above commands. The script requires installation of `paramiko` and `scp` on the host. The usage is `python3 download_all.py [data size] [start ip addresss] [number of nodes] -k [service-key file] -t [number of threads]`. For example, to download and decompress 30TB data for machines from IP 10.128.0.10 to 49.128.0.49 

```sh
sudo pip3 install paramiko scp
python3 download_all.py 30k 10.128.0.10 40
```

&nbsp;
## Load, Run and Update
Please refer to the the [parent page](../) for the installation of TigerGraph. 
Default setting can get random errors during loading because FileLoader timeout too small. 
Before loading, config the timeout limit is required
```sh
gadmin config entry GPE.BasicConfig.Env
# add MVExtraCopy=0; (default is 1) This turns off backup copy.

gadmin config group timeout
# Change FileLoader.Factory.HandlerCount: 16 -> 100
# Change KafkaLoader.Factory.DefaultQueryTimeoutSec: 16 -> 6000
# Change RESTPP.Factory.DefaultQueryTimeoutSec: 16 -> 6000
gadmin config apply -y
gadmin restart -y
```

The dataset does not have header. For 10T data, just replace `~/sf30k` with `~/sf10k`. To load the data in background(take ~12hr)
```sh
nohup python3 -u ./driver.py load all ~/sf30k > foo.out 2>&1 < /dev/null &
```
Run queries and perform the batch update, begin date is `2012-11-29`, end date is `2012-12-31`. We perform bi reading queries every 7 days, we also add sleep factor 1. 
```sh
nohup python3 -u ./driver.py refresh ~/sf30k -q reg:bi* -b 2012-11-29 -e 2012-12-31 -r 7 -s 0.5 > foo.out 2>&1 < /dev/null & 
```

The combined command in background is
```sh
nohup python3 -u ./driver.py bi ~/sf30k -q reg:bi* -b 2012-11-29 -e 2012-12-31 -r 7 -s 1  > foo.out 2>&1 < /dev/null & 
```

&nbsp;
## About queries
The BI queries on 10TB data is typically ~60 s and greatly depends on the parameters. We chose some parameters that are easy for use, for example if we filter the comments after an input date, we will chose a later time for the Social network graph.

BI20 have several version. The query is fast for some parameters (in this case, the non-distributed one `bi20-1.gsql` takes less time). But the query is super slow for other parameters (>200s, in this case, the distributed one `bi20-2.gsql` is better). We have not validated `bi20-3` yet.
