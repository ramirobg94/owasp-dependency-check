import { SET_STATUS,
 CHECK_URL_ATTEMPT, CHECK_URL_SUCCESS,CHECK_URL_FAIL,
  CHECK_STATUS_ATTEMPT, CHECK_STATUS_SUCCESS, CHECK_STATUS_FAIL,
  CHECK_RESULTS_ATTEMPT, CHECK_RESULTS_SUCCESS, CHECK_RESULTS_FAIL
  } from './actionTypes';

export * from './actions';

const initialState = 0;
function status(state= initialState, action){
  switch(action.type){
    case SET_STATUS:
    console.log("setStatus", action)
      return action.details;
    case CHECK_URL_SUCCESS:
    	var newState = 1;
    	return newState;
    case CHECK_STATUS_SUCCESS:
      var newState = action.status;
      return newState;
    case CHECK_RESULTS_SUCCESS:
      var newState = action.status;
      return newState;
    default:
      return state;
  }
}

export default status