import { SET_FILTER_LEVEL, SET_FILTER_ORDER } from './actionTypes';

export function setFilterLevel(details){
  return {
    type: SET_FILTER_LEVEL,
    details: details
  }
}

export function setFilterOrder(details){
  return {
    type: SET_FILTER_ORDER,
    details: details
  }
 }