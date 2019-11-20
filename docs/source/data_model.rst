==========
Data Model
==========

Inside CoTeDe, the dataset to be analyzed is treated as a single object that contains all variables (temperature, salinity, fluorescence, ...), coordinates (pressure, depth, ...), and metadata. 
This data model is the same independent of the sampling platform, therefore, temperature measurements collected by an XBT, a Spray glider, a CTD rosette, a mooring or a Saildrone are all accessed in the same way.
The difference is that each case might use a different set of QC tests, and each test decides what should be used to evaluate the quality of the dataset.

Other applications can connect with CoTeDe by providing the data using this data model. 
For example, `pySeabird <http:/seabird.castelao.net>`_ is another Python package able to parse CTD raw data and organize it as described on this session before calling CoTeDe to QC the profiles.

Data
~~~~

Each variable is expected to be accessible as an item of the dataset object, and it should return a sequence, preferably a numpy array. 
Considering a dataset named 'ds', to access the temperature::

  $ ds['TEMP']
  >>> masked_array(data=[17, 16.8, 16], mask=False, fill_value=1e+20)

Coordinates and other auxiliary variables with the same dimension of the variable of interest should be available on the same way, thus for a profile the depth of each measurement would be accessible as::

  $ ds['DEPTH']
  >>> masked_array(data=[0, 10, 20], mask=False, fill_value=999999)

Metadata
~~~~~~~~

Scalar metadata representative for the whole dataset should be available in the property attrs. For example, to obtain the nominal time of a CTD cast::

  $ ds.attrs['datetime']
  >>> datetime.datetime(2019, 11, 22, 5, 15, 57, 619332)
  >>> numpy.datetime64('2019-11-22T05:16:56.932129')

or the nominal latitude of a mooring::

  $ ds.attrs['latitude']
  >>> 15

but if latitude has the same dimension of the data, like the along track latitude for a TSG, it should be available together with the data, like::

  $ ds['latitude']
  >>> masked_array(data=[14.998, 15.0, 15.001], mask=False, fill_value=np.nan)


.. note::

    Numpy masked array is the prefered choice. In that case, whatever is masked
    will be considered that the data is unavailable. If not using masked arrays
    , missing data should be assigned with np.nan.

Minimalist solution
~~~~~~~~~~~~~~~~~~~

Possibly the simplest model to achieve that is::

  class CoTeDeDataset(object):
    def __init__(self):
        self.attrs = {}
        self.data = {}

    def __getitem__(self, key):
        return self.data[key]

    def keys(self):
        return self.data.keys()

So that::

  $ ds = CoTeDeDataset()
  $ ds.data['TEMP'] = np.array([15, 14.8, 14.3])
  $ ds.attrs['longitude'] = -38
  ...

Check the `data model notebook <https://github.com/castelao/CoTeDe/tree/master/docs/notebooks>`_ for a complete example on how to use it.        
