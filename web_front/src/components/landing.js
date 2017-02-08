import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import ResultListItem from './results/resultListItem';
import ResultList from './results/resultList';
import SearchBar from './searchBar';

class Landing extends Component{
	constructor(props){
		super(props);
	}

	render(){
		return(
			<div id="layout">
				<SearchBar/>
				<ResultList/>
			</div>
		)
	}
}

export default Landing;
