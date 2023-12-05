
"""
Various utility functions for mapping constrained sensors locations with the column indices for class GQR.
"""

import numpy as np
import pandas as pd
import sys, os


def get_constraind_sensors_indices(x_min, x_max, y_min, y_max, nx, ny, all_sensors):
    """
    Function for mapping constrained sensor locations on the grid with the column indices of the basis_matrix.

    Parameters
    ----------
    x_min: int, lower bound for the x-axis constraint
    x_max : int, upper bound for the x-axis constraint
    y_min : int, lower bound for the y-axis constraint
    y_max : int, upper bound for the y-axis constraint
    nx : int, image pixel (x dimensions of the grid)
    ny : int, image pixel (y dimensions of the grid)
    all_sensors : np.ndarray, shape [n_features], ranked list of sensor locations.

    Returns
    -------
    idx_constrained : np.darray, shape [No. of constrained locations], array which contains the constrained
        locations of the grid in terms of column indices of basis_matrix.
    """
    n_features = len(all_sensors)
    image_size = int(np.sqrt(n_features))
    a = np.unravel_index(all_sensors, (nx,ny))
    constrained_sensorsx = []
    constrained_sensorsy = []
    for i in range(n_features):
        if (a[0][i] >= x_min and a[0][i] <= x_max) and (a[1][i] >= y_min and a[1][i] <= y_max):
            constrained_sensorsx.append(a[0][i])
            constrained_sensorsy.append(a[1][i])

    constrained_sensorsx = np.array(constrained_sensorsx)
    constrained_sensorsy = np.array(constrained_sensorsy)
    constrained_sensors_array = np.stack((constrained_sensorsy, constrained_sensorsx), axis=1)
    constrained_sensors_tuple = np.transpose(constrained_sensors_array)
    if len(constrained_sensorsx) == 0: ##Check to handle condition when number of sensors in the constrained region = 0
        idx_constrained = []
    else:
        idx_constrained = np.ravel_multi_index(constrained_sensors_tuple, (nx,ny))
    return idx_constrained

def get_constrained_sensors_indices_linear(x_min, x_max, y_min, y_max,df):
    """
    Function for obtaining constrained column indices from already existing linear sensor locations on the grid.

    Parameters
    ----------
    x_min: int, lower bound for the x-axis constraint
    x_max : int, upper bound for the x-axis constraint
    y_min : int, lower bound for the y-axis constraint
    y_max : int, upper bound for the y-axis constraint
    df : pandas.DataFrame, a dataframe containing the features  and samples

    Returns
    -------
    idx_constrained : np.darray, shape [No. of constrained locations], array which contains the constrained
        locations of the grid in terms of column indices of basis_matrix.
    """
    x = df['X (m)'].to_numpy()
    n_features = x.shape[0]
    y = df['Y (m)'].to_numpy()
    idx_constrained = []
    for i in range(n_features):
        if (x[i] >= x_min and x[i] <= x_max) and (y[i] >= y_min and y[i] <= y_max):
            idx_constrained.append(i)
    return idx_constrained

def get_constrained_sensors_indices_distance(j,piv,r, nx,ny, all_sensors):
    """
    Function for mapping constrained sensor locations on the grid with the column indices of the basis_matrix.
    Parameters
        ----------
        all_sensors : np.ndarray, shape [n_features]
            Ranked list of sensor locations.
        Returns
        -------
        idx_constrained : np.darray, shape [No. of constrained locations]
            Array which contains the constrained locationsof the grid in terms of column indices of basis_matrix.
    """
    n_features = len(all_sensors)
    image_size = int(np.sqrt(n_features))
    a = np.unravel_index(piv, (nx,ny))
    t = np.unravel_index(all_sensors, (nx,ny))
    x_cord = a[0][j-1]
    y_cord = a[1][j-1]
    #print(x_cord,y_cord)
    constrained_sensorsx = []
    constrained_sensorsy = []
    for i in range(n_features):
        if ((t[0][i]-x_cord)**2 + (t[1][i]-y_cord)**2) < r**2:
            constrained_sensorsx.append(t[0][i])
            constrained_sensorsy.append(t[1][i])

    constrained_sensorsx = np.array(constrained_sensorsx)
    constrained_sensorsy = np.array(constrained_sensorsy)
    constrained_sensors_array = np.stack((constrained_sensorsx, constrained_sensorsy), axis=1)
    constrained_sensors_tuple = np.transpose(constrained_sensors_array)
    if len(constrained_sensorsx) == 0: ##Check to handle condition when number of sensors in the constrained region = 0
        idx_constrained = []
    else:
        idx_constrained = np.ravel_multi_index(constrained_sensors_tuple, (nx,ny))
    return idx_constrained

def functional_constraints(functionHandler, idx,kwargs):
    """
    Function for evaluating the functional constraints.

    Parameters
    ----------
    functionHandler : function, a function handle to the function which is to be evaluated
    idx : np.ndarray, ranked list of sensor locations (column indices)
    shape : tuple of ints, Shape of the matrix fed as data to the algorithm
    data : pandas.DataFrame, Dataframe which represents the measurement data.

    Return
    ------
    g : function, Contains the function defined by the user for the functional constraint. 
    """
    if 'shape' in kwargs.keys():
        shape = kwargs['shape']
        xLoc,yLoc = get_coordinates_from_indices(idx,shape)
    elif 'data' in kwargs.keys():
        data = kwargs['data']
        ## TODO:
        #xLoc = data.loc[idx, 'X (m)']
        #yLoc = data.loc[idx, 'Y (m)']
        xLoc,yLoc =  get_indices_from_dataframe(idx,data)
    functionName = os.path.basename(functionHandler).strip('.py')
    dirName = os.path.dirname(functionHandler)
    sys.path.insert(0,os.path.expanduser(dirName))
    module = __import__(functionName)
    func = getattr(module, functionName)
    g = func(xLoc, yLoc,**kwargs)
    return g

def constraints_eval(constraints,senID,**kwargs):
    """
    Function for evaluating whether a certain sensor index lies within the constrained region or not.

    Parameters:
    ---------- 
        constraints: __(type?)__, The constraint defined by the user 
        senID: np.ndarray, shape [n_features], ranked list of sensor locations (column indices)
        data : pandas.DataFrame/np.ndarray shape [n_features, n_samples]
                Dataframe or Matrix which represent the measurement data.
    Returns
    -------
    G : Boolean np.darray, shape [n_features], array which contains a Boolean value based on whether a column index is constrained or not.
    """
    nConstraints = len(constraints)
    G = np.zeros((len(senID),nConstraints),dtype=bool)
    for i in range(nConstraints):
        temp = functional_constraints(constraints[i],senID,kwargs)
        G[:,i] = [x>=0 for x in temp]

    return G

def get_functionalConstraind_sensors_indices(senID,g):
    """
    Function for finding constrained sensor locations on the grid and their ranks

    Parameters
    ----------
    senID: np.darray, ranked list of sensor locations (column indices)
    g : float, constraint evaluation function (negative if violating the constraint)

    Returns
    -------
    idx_constrained : np.darray, shape [No. of constrained locations], array which contains the constrained
        locations of the grid in terms of column indices of basis_matrix.
    rank : np.darray, shape [No. of constrained locations], array which contains rank of the constrained sensor locations
    """
    assert (len(senID)==len(g))
    idx_constrained = senID[~g].tolist()
    rank = np.where(np.isin(senID,idx_constrained))[0].tolist() # ==False
    return idx_constrained, rank

def order_constrained_sensors(idx_constrained_list, ranks_list):
    """
    Function for ordering constrained sensor locations on the grid according to their ranks.

    Parameters
    ----------
    idx_constrained_list : np.darray shape [No. of constrained locations], Constrained sensor locations
    ranks_list : no.darray shape [No. of constrained locations], Ranks of each constrained sensor location

    Returns
    -------
    sortedConstraints : np.darray, shape [No. of constrained locations], array which contains the constrained
        locations of the grid in terms of column indices of basis_matrix sorted according to their rank.
    ranks : np.darray, shape [No. of constrained locations], array which contains the ranks of constrained sensors. 
    """
    sortedConstraints,ranks =zip(*[[x,y] for x,y in sorted(zip(idx_constrained_list, ranks_list),key=lambda x: (x[1]))])
    return sortedConstraints,ranks

def get_coordinates_from_indices(idx,info):
    """
    Function for obtaining the coordinates on a grid from column indices
    
    Parameters
    ----------
    idx :  int, sensor ID
    info : pandas.DataFrame/np.ndarray shape [n_features, n_samples], Dataframe or Matrix which represent the measurement data.

    Returns
    -------
    idx_constrained : np.darray, shape [No. of constrained locations], array which contains the constrained
        locations of the grid in terms of column indices of basis_matrix.

    Returns:
        (x,y) : tuple, The coordinates on the grid of each sensor. 
    """
    if isinstance(info,tuple):
        return np.unravel_index(idx,info,'F')
    elif isinstance(info,pd.DataFrame):
        x = info.loc[idx,'X (m)']#.values
        y = info.loc[idx,'Y (m)']#.values
        return (x,y)

def get_indices_from_coordinates(coordinates,shape):
    """
    Function for obtaining the indices of columns/sensors from coordinates on a grid when data is in the form of a matrix
    
    Parameters
    ----------
    coordinates : tuple of array_like , (x,y) pair coordinates of sensor locations on the grid
    shape : tuple of ints, Shape of the matrix fed as data to the algorithm

    Returns
    -------
    np.ravel_multi_index(coordinates,shape,order='F') : np.ndarray, The indices of the sensors. 
    """
    return np.ravel_multi_index(coordinates,shape,order='F')

def get_indices_from_dataframe(idx,df): ## Niharikas_comment : I think this should be renamed to get coordinates from dataframe as when given a sensor index it returns a tuple containing the coordinates of that sensor index.
    ## It can also maybe be removed completely as get_coordinates_from_indices(idx,info) does the same thing. Thoughts? 
    
    x = df['X (m)'].to_numpy()
    y = df['Y (m)'].to_numpy()
    return(x[idx],y[idx])

if __name__ == '__main__':

    import pysensors as ps
    from sklearn import datasets

    # Test the constraintsEval function
    const1 = '~/projects/pysensors/examples/userExplicitConstraint1.py'
    const2 = '~/projects/pysensors/examples/userExplicitConstraint2.py'
    constList = [const1, const2]
    faces = datasets.fetch_olivetti_faces(shuffle=True)
    XX = faces.data
    n_samples, n_features = XX.shape
    # Global centering
    XX = XX - XX.mean(axis=0)
    # Local centering
    XX -= XX.mean(axis=1).reshape(n_samples, -1)

    n_sensors0 = 15
    n_modes0 = 15
    basis1 = ps.basis.SVD(n_basis_modes=n_modes0)
    optimizer_faces = ps.optimizers.QR()
    model = ps.SSPOR(basis=basis1,optimizer=optimizer_faces, n_sensors=n_sensors0)
    model.fit(XX)
    basis_matrix = model.basis_matrix_

    all_sensors0 = model.get_all_sensors()
    top_sensors0 = model.get_selected_sensors()

    xTopUnc = np.mod(top_sensors0,np.sqrt(n_features))
    yTopUnc = np.floor(top_sensors0/np.sqrt(n_features))
    xAllUnc = np.mod(all_sensors0,np.sqrt(n_features))
    yAllUnc = np.floor(all_sensors0/np.sqrt(n_features))

    # sensors_constrained = ps.utils._constraints.get_constraind_sensors_indices(xmin,xmax,ymin,ymax,nx,ny,all_sensors0) #Constrained column indices
    G = ps.utils._constraints.constraints_eval(constList,top_sensors0,shape=(64,64))
    idx_constrainedConst,ranks = ps.utils._constraints.get_functionalConstraind_sensors_indices(top_sensors0,G[:,0])
    idx_constrainedConst2,rank2 = ps.utils._constraints.get_functionalConstraind_sensors_indices(top_sensors0,G[:,1])

    idx_constrainedConst.extend(idx_constrainedConst2)
    ranks.extend(rank2)
    idx_constr_sorted, ranks = ps.utils._constraints.order_constrained_sensors(idx_constrainedConst,ranks)

    n_const_sensors0 = 1
    optimizer1 = ps.optimizers.GQR()
    opt_kws={'idx_constrained':idx_constrainedConst,
             'n_sensors':n_sensors0,
             'n_const_sensors':n_const_sensors0,
             'all_sensors':all_sensors0,
             'constraint_option':"max_n"}
    model1 = ps.SSPOR(basis = basis1, optimizer = optimizer1, n_sensors = n_sensors0)
    model1.fit(XX,**opt_kws)
    basis_matrix_svd = model1.basis_matrix_
    all_sensors1 = model1.get_all_sensors()

    top_sensors = model1.get_selected_sensors()
    print(top_sensors)
    dterminant_faces_svd = ps.utils._validation.determinant(top_sensors,n_features,basis_matrix_svd)
    print(dterminant_faces_svd)


    const3 = '/Users/abdomg/projects/Sparse_Sensing_in_NDTs_LDRD/notebooks/myBoxConstraint.py'
    constList2 =[const3]
    constr_kws = {'xmin':10,'xmax':30,'ymin':20,'ymax':40,'shape':(64,64)}
    G2 = ps.utils._constraints.constraints_eval(constList2,all_sensors0,**constr_kws)