import { LOAD_VULNERABILITIES_SUCCESS } from './actionTypes';

export function loadVulnerabilities(details){
  return {
    type: LOAD_VULNERABILITIES_SUCCESS,
    vulnerabilities: details
  }
}

