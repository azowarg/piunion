#! /usr/local/bin/bash
for i in {1..17}
do
DATE="$i.02.2023"
CURRENCY="AVAX"
echo "$DATE"
echo "$DATE,$(curl -s "https://min-api.cryptocompare.com/data/pricehistorical?fsym=${CURRENCY}&tsyms=EUR&ts=$(date -j -f "%d.%m.%Y %H:%M:%S" "${DATE} 06:00:00" +%s)" | yq .${CURRENCY}.EUR)" >> $CURRENCY.csv
done