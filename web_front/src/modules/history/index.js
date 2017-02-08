import { LOAD_HISTORY_SCANS_ATTEMPT, LOAD_HISTORY_SCANS_SUCCESS, LOAD_HISTORY_SCANS_FAIL,
SET_HISTORY_PAGE } from './actionTypes';

export * from './actions';


const initialState = [];
function histories(state=[], action){
  switch(action.type){
    case LOAD_HISTORY_SCANS_SUCCESS: 
      return action.histories;
    default:
      return state;
  }
}

const initialError = false;
function error(state=initialError, action){
  switch(action.type){
    case LOAD_HISTORY_SCANS_SUCCESS: 
    case LOAD_HISTORY_SCANS_ATTEMPT:
      return false;
    case LOAD_HISTORY_SCANS_FAIL:
   	  return true;
    default:
      return state;
  }
}

const initialPage = 1;
function page(state=initialPage, action){
	switch(action.type){
    case SET_HISTORY_PAGE: 
      return action.page;
    default:
      return state;
  }
}

const initialLoading = false;
function loadingHistories(state=initialLoading, action){
	switch(action.type){
    case LOAD_HISTORY_SCANS_SUCCESS:
   	case LOAD_HISTORY_SCANS_FAIL:
      return false;
    case LOAD_HISTORY_SCANS_ATTEMPT:
      return true;
    default:
      return state;
  }
}

export default vulnerabilities