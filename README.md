** This is not production code, it's an experiment **

# Set up

You will need:
* Python 2.7 or greater
* virtualenv
* `client_secrets.json` from [Google API Console](https://code.google.com/apis/console)

Then run `setup.sh` and follow any instructions.

# The query API

The naming follows relatively closely to that of Google Analytics.

`start-at`:   An ISO8601 date time, not required, if it's not provided no lower bound is applied.
`end-at`:     An ISO8601 date time, not required, if it's not provided no upper bound is applied.
`dimensions`: A list of fields the data should be 'grouped' by. Default: empty list.
`metrics`:    A list of fields containing numeric data that should be present. Required.
`period`:     How long each time period is. Required (although ideally wouldn't be). (hour, day, week)

** Notes **

1. Because metrics like visits and visitors cannot be aggregated we need to store all combinations of dimensions and period
   separately. This is done for format engagement format and slug. This could obviously grow pretty quickly as we add more
   dimensions and periods.