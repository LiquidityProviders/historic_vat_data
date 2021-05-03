# Pull Vat Data
This repository is used to retrieve historical Vat Dai balances from the Vulcanize API. To learn more about Graphql and Vulcanize see https://maker-data-api-documentation.now.sh/documentation

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

## auditing review:
 FOR AUDITING REVIEW: Anyone of the transaction hashes associated with the address Dai balance could have the Vat data state changing. So if you want to perfomr this check on your own it may require you trying each individual 'hash' which is a direct reference to the transaction that took place on the Ethereum blockchain.

 To perform this manually via a UI:
 1. Visit https://dashboard.tenderly.co/explorer and then enter in the 'hash' associated with the state change into the main search field.
 2. Once the Tx is searched for... click 'State Changes' on the left hand side.
 3. You have found the correct TX hash if the address associated with it in the list below is what shows up in the 'dai' box in the UI.
 4. In the UI copy the green integer value associated with the correct address and perform the following equation : DAI_VALUE_IN_UI / 10^18 to get the correct DAI amount that address had in the Vat contract.

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


```
Old query:
 query($pageSize: Int, $address: String) {
   allVatDais(first:$pageSize,
     condition:{guy: $address}) {
     nodes {
       dai
       headerByHeaderId {
         blockNumber
       }
     }
   }
 }
```

```
New query:
 query ($pageSize: Int, $address: String, numOfTx: $numOfTx){
    allVatDais(first:1000,
      condition:{guy: "0xe51A8FeCfc17F7a6c1eEd2BfeA2dB20Cb850C922"}) {
      nodes {
        dai
        headerByHeaderId {
          blockNumber
           transactionsByHeaderId(first:100) {
             nodes {
               hash
               txFrom
               txTo
             }
           }
        }
      }
    }
  }
```

