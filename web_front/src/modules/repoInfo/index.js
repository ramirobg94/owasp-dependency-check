import { LOAD_URL, LOAD_ID, LOAD_TEST } from './actionTypes';

export * from './actions';


const initialState = {
  url: '',
  id: null,
  total_tests: 0,
  passed_tests: 0
}
function repoInfo(state= initialState, action){
  switch(action.type){
    case LOAD_URL:
      return Object.assign({}, state, action.payload);
    case LOAD_ID:
      return Object.assign({}, state, action.payload);
    case LOAD_TEST:
      return Object.assign({}, state, action.payload);
    default:
      return state;
  }
}

export default repoInfo;