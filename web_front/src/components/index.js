import React, { Component, PropTypes } from 'react';
import {Router,Route, IndexRoute, browserHistory} from 'react-router';

import Layout from './layout';
import Landing from './landing';

import History from './history';
import Search from './search';
import Project from './project';


class DepChecker extends Component {
  constructor(props){
    super(props)
  }
  render(){

    return(
    <Router history={browserHistory}> 
      <Route path='/' component={ Layout} > 
        <IndexRoute component={ Landing } />
        <Route path='history' component={ History } />
        <Route path='search' component={ Search } />
        <Route path='project' component={ Project } />
      </Route>
    </Router> 
      )
  }
    
}

export default DepChecker;