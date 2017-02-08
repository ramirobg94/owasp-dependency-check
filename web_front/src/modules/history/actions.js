import { LOAD_HISTORY_SCANS_ATTEMPT, LOAD_HISTORY_SCANS_SUCCESS, LOAD_HISTORY_SCANS_FAIL,
SET_HISTORY_PAGE } from './actionTypes';

export function setPage(details){
  return (dispatch) => {

  	dispatch({
      type: LOAD_VULNERABILITIES_SUCCESS,
    	page: details
    });

  	dispatch(loadHistory(details))
    
 }
}

export function loadHistory(details){

  return (dispatch) => {

    dispatch({
      type: LOAD_HISTORY_SCANS_ATTEMPT
    });
 
    get('/api/v1/project/results/'+details)
    .then( response => {
      dispatch({
        type: LOAD_HISTORY_SCANS_SUCCESS,
        histories: response.scans
      });
    })
    .catch( err => {   
      dispatch({
        type: LOAD_HISTORY_SCANS_FAIL,
        error: err
      })
    })

  }

}