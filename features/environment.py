from behave import fixture
import os
from shutil import copyfile
from Onaeri import settings


@fixture
def before_all(context):
    context.cleanup = []
    context.cycleNames = ['test-case-A', 'test-case-B',
                          'test-case-C', 'test-case-D']

    print("Creating settings files:")
    template = os.getcwd() + "/Onaeri/settings/Template.py"
    for name in context.cycleNames:
        dst = os.getcwd() + "/Onaeri/settings/%s.py" % name
        copyfile(template, dst)
        print("\t%s" % dst)
        context.cleanup.append(dst)  # Mark file for cleanup
    settings.cycles = settings._settingFileList()  # Reload setting files


@fixture
def after_all(context):
    print("Cleaning up:", flush=True)
    for path in context.cleanup:
        print("\t%s" % path, flush=True)
        os.remove(path)

    print("\tDynamic setting files:")
    folder = os.getcwd() + "/Onaeri/settings/dynamic"
    files = [f for f in os.listdir(folder)
             if os.path.isfile(os.path.join(folder, f))
             and not f.startswith(".") and f.endswith(".json")]
    for f in files:
        print("\t\t", f, flush=True)
        f = "%s/%s" % (folder, f)
        os.remove(f)
