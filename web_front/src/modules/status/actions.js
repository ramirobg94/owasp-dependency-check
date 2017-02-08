import { SET_STATUS,
 CHECK_URL_ATTEMPT, CHECK_URL_SUCCESS,CHECK_URL_FAIL,
 CHECK_STATUS_ATTEMPT, CHECK_STATUS_SUCCESS, CHECK_STATUS_FAIL,
 CHECK_RESULTS_ATTEMPT, CHECK_RESULTS_SUCCESS, CHECK_RESULTS_FAIL
  } from './actionTypes';
import {get} from '../../lib/api';

import { loadId,loadTests } from '../repoInfo';
import { loadVulnerabilities } from '../vulnerabilities';


export function setStatus(details){
  return {
    type: SET_STATUS,
    details: details
  }
}

export function checkUrl(details){

  return (dispatch) => {

    dispatch({
      type: CHECK_URL_ATTEMPT
    });

    get('/api/v1/project/create?lang=nodejs&repo='+details+'&type=git')
    .then(response => {
      
      dispatch({
        type: CHECK_URL_SUCCESS
      });

      dispatch(loadId(response.project))


    })
    .catch( err => {
      dispatch({
        type: CHECK_URL_FAIL,
        error: err
      })
    })
  }
}

export function checkStatus(details){

  return (dispatch) => {

    dispatch({
      type: CHECK_STATUS_ATTEMPT
    });

    get('/api/v1/project/status/'+details)
    .then(response => {
      const posibleStatus= ['start','created','running','finished','non-accessible', 'results'];
      var newStatus = posibleStatus.indexOf(response.scan_status)
    
      dispatch({
        type: CHECK_STATUS_SUCCESS,
        status: newStatus
      });

        dispatch(loadTests({
        total_tests: response.total_tests,
        passed_tests: response.passed_tests
      }))

        if(response.scan_status == 'finished'){
          dispatch(checkResults(details))
        }

    })
    .catch( err => {
      dispatch({
        type: CHECK_STATUS_FAIL,
        error: err
      })
    })
  }
}

export function checkResults(details){

  return (dispatch) => {

    dispatch({
      type: CHECK_RESULTS_ATTEMPT
    });
 
    get('/api/v1/project/results/'+details)
    .then(response => {
      const posibleStatus= ['start','created','running','finished','non-accessible', 'results'];
       var newStatus = posibleStatus.indexOf('finished')
      
      dispatch({
        type: CHECK_RESULTS_SUCCESS,
        status: newStatus
      });

      dispatch(loadVulnerabilities(response.vulnerabilities))


    })
    .catch( err => {
      dispatch({
        type: CHECK_RESULTS_FAIL,
        error: err
      })
    })
  }
}