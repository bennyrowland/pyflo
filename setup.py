from distutils.core import setup

setup(
        name='pyflo',
        version='0.0.1',
        packages=['pyflo', 'tests'],
        url='',
        license='',
        author='ben',
        author_email='bennyrowland@mac.com',
        description='',
        entry_points={
            "pyflo": [
                "pyflo.string.split = pyflo.components.string.string:SplitComponent",
                "pyflo.string.format = pyflo.components.string.string:FormatComponent",
                "pyflo.core.readfile = pyflo.components.core:FileReadComponent",
                "pyflo.core.log = pyflo.components.core:ConsoleLoggerComponent",
                "pyflo.core.count = pyflo.components.core:CountingComponent",
                "pyflo.core.graph = pyflo.components.core:GraphComponent",
            ],
            "pyflo.loaders": [
                "couchdb = pyflo.loaders:CouchDBSource",
            ],
            "console_scripts": [
                "pyflo = pyflo.main:run_graph",
                "pyflo-library = pyflo.main:export_components"
            ]
        },
        install_requires=["stevedore", 'pycouchdb', 'pytest']
)
