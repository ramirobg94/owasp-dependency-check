import { LOAD_VULNERABILITIES_SUCCESS } from './actionTypes';

export * from './actions';

function vulnerabilities(state=[], action){
  switch(action.type){
    case LOAD_VULNERABILITIES_SUCCESS: 
      return action.vulnerabilities;
    default:
      return state;
  }
}


export default vulnerabilities