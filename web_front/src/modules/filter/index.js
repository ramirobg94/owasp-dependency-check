import { SET_FILTER_LEVEL, SET_FILTER_ORDER } from './actionTypes';
import  { combineReducers } from 'redux';

export * from './actions';

const initialSate = ['low','medium','high', 'unknown'];
function levels(state = initialSate, action){
  switch(action.type){
    case SET_FILTER_LEVEL:

      //var newStateObj = Object.assign({}, state);
     // var newState = Object.keys(newStateObj).map(function (key) { return newStateObj[key]; });
     console.log("prev state", state)
      var newState = state.slice();
      if(newState.indexOf(action.details) >= 0){
        newState.splice(newState.indexOf(action.details),1)
      }else{
        newState.push(action.details)
      }
      return newState;

    default:
      return state;
  }
}

const initialStateOrder = 0;
function order(state= initialStateOrder, action){
  switch(action.type){
    case SET_FILTER_ORDER:

      if(state == action.details){
        return state;
      }else{
        return action.details;
      }
    case SET_FILTER_LEVEL:
      return state;
    default:
      return state;
  }
}

export default combineReducers({
  levels,
  order
})