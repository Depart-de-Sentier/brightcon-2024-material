import bw2data as bd
import bw2io as bi
import inspect
from blinker import signal
from importlib.metadata import version

# dl stands for data lineage
# bw2data has to be installed so far from branch data_lineage e.g. with:
# pip install -e git+https://github.com/cswh/brightway2-data.git@data_lineage


def dl_emit_database_written(datastore):
    db_physical_location = str(bd.projects.dir / "lci/databases.db")
    db_abstract_name = datastore.name
    tmp = inspect.stack()
    input_location = "".join([str(i.frame.f_locals.get("lci_path","")) for i in tmp])
    function_call = print("\n".join([" ".join(["function", i.function, "from", str(inspect.getmodule(i.frame))]) for i in tmp]))
    print(" ".join(["writing", db_physical_location, db_abstract_name]))
    version("bw2data")
    version("bw2io")
    "TODO: something meaningful with client.emit"

def dl_emit_activity_saved(activity_dataset):
    db_physical_location = str(bd.projects.dir / "lci/databases.db")
    db_physical_table_name = "activitydataset"
    db_abstract_name = activity_dataset.database
    act_identifier = str(activity_dataset.key)
    print(" ".join(["updating", act_identifier, db_abstract_name, db_physical_table_name, db_physical_location]))
    "TODO: something meaningful with client.emit"

def dl_emit_exchange_saved(exchange_dataset):
    db_physical_location = str(bd.projects.dir / "lci/databases.db")
    db_physical_table_name = "exchangedataset"
    input_identifier = str((exchange_dataset.input_database, exchange_dataset.input_code))
    output_identifier = str((exchange_dataset.output_database, exchange_dataset.output_code))
    print(" ".join(["updating", input_identifier, output_identifier, db_physical_table_name, db_physical_location]))
    "TODO: something meaningful with client.emit"

signal("bw2data.database_written").connect(dl_emit_database_written)
signal("bw2data.activity_saved").connect(dl_emit_activity_saved)
signal("bw2data.exchange_saved").connect(dl_emit_exchange_saved)

# testing for setting up a brightway project
bd.projects.set_current("test7")
bi.import_ecoinvent_release("3.10", "cutoff")

# testing for changing an activity or exchange
db = bd.Database("ecoinvent-3.10")
act = db.random()
act.save()
act.copy()