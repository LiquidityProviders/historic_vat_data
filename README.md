# Pull Vat Data
This repository is used to retrieve historical Vat Dai balances.

## setup
```
git clone https://github.com/LiquidityProviders/historic_vat_data.git
cd historic_vat_data
./install.sh
```

go to https://observablehq.com/@levity/search-for-a-block-by-timestamp and enter in the timestamp you would like Vat data for

Enter in the block number returned by the link above into the start script below as the `--before-or-equal-block` argument.

Ensure you have created the startfile and added it to the homedirectory of the repo (see example startfile below).

Run the startfile:
```
./start.sh
```

## example start file:
```
#!/bin/bash

source ./env
source ./_virtualenv/bin/activate || exit
dir="$(dirname "$0")"
export PYTHONPATH=$PYTHONPATH:$dir:$dir/lib/pymaker

exec python3 -m pull_vat_data.main \
    --before-or-equal-block 11565018 \
    --auction-config 'auction_config_2020.json' \
    --vulcanize-api-key ${VULCANIZE_API_KEY:?} \
    $@ 2> >(tee -a ${LOGS_DIR:?}/vat_balances.log >&2)
```


