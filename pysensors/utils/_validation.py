"""
Various utility functions for validation and computing reconstruction scores and errors.
"""
import numpy as np

def determinant(top_sensors, n_features, basis_matrix):
    """
    Function for calculating |C.T phi.T C phi|.

    Parameters
        ----------
        top_sensors: np.darray,
            Column indices of choosen sensor locations
        n_features : int,
            No. of features of dataset
        basis_matrix : np.darray,
            The basis matrix calculated by model.basis_matrix_
        
        Returns
        -------
        optimality : Float, 
            The dterminant value obtained.
    """
    
    c = np.zeros([len(top_sensors),n_features])
    print(c.shape)
    for i in range(len(top_sensors)):
        c[i,top_sensors[i]] = 1
    print(c)
    phi = basis_matrix
    optimality = np.linalg.det((c@phi).T @ (c@phi))
    print(optimality)
    return (c,phi,optimality)

def relative_reconstruction_error(data, prediction):
    """
    Function for calculating relative error between actual data and the reconstruction

    Parameters
        ----------
        data: np.darray,
            The actual data from the dataset evaluated 
        prediction : np.darray,
            The predicted values from model.predict(X[:,top_sensors])
        Returns
        -------
        error_val : Float, 
            The relative error calculated.
    """
    error_val = (np.linalg.norm((data - prediction)/np.linalg.norm(data)))*100
    print(error_val)
    return (error_val)