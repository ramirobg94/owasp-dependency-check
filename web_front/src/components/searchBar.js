import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import {Link} from 'react-router';

import { loadUrl } from '../modules/repoInfo';
import { checkUrl, checkStatus, checkResults, setStatus } from '../modules/status';

import Status from './status';
import ErrorBox from './errorBox';
import Resume from './resume';


import HistoryListItem from './history/historyListItem';

class SearchBar extends Component{
	constructor(props){
		super(props);
		this.handleFieldChange = this.handleFieldChange.bind(this);
		this.handleSubmit = this.handleSubmit.bind(this);
		this.handleStatus = this.handleStatus.bind(this);
		this.handleResults = this.handleResults.bind(this);
		this.showResults = this.showResults.bind(this);
	}

	handleFieldChange(e){
		this.props.loadUrl({
			[e.target.name]: e.target.value
		});
	}

	handleSubmit(e){
		e.preventDefault();
		this.props.checkUrl(this.props.url);
	}

	handleStatus(e){
		this.props.checkStatus(this.props.id);
	}

	handleResults(e){
		this.props.checkResults(this.props.id);
	}

	showResults(e){
		e.preventDefault();
		this.props.setStatus(5);
	}


	render(){

		const StatusBox = this.props.status > 0 && this.props.status < 3 ? 
			<Status 
			status={this.props.status} 
			checkStatus={this.handleStatus} 
			totalTests={this.props.totalTests}
			passedTest={this.props.passedTest} /> 
				:  ( this.props.status == 4 ? 
					<ErrorBox/> 
					: ( this.props.status == 3 ? 
						<Resume
						urlProject={this.props.url}
						idProject={this.props.id}
						totalTests={this.props.totalTests}
						vulnerabilities={this.props.vulnerabilities}
						showResults={this.showResults}/> 
						: '')
			);

		return(
		<div id="searchBox" style={{height: this.props.status == 5 ? 120 : 'calc(100vh - 50px)'}}>
			<div className="overLay">

				<div id="searchBarBox" style={{top: this.props.status > 0 ? 50 : "7vh"}}>

					<div id="indexText" className="text-center" style={{ display: this.props.status > 0 ? 'none' : 'block'}}>
						<h1>Comprueba que librerías de tu software son inseguras</h1>
						<h2> Introduce la url de github</h2>
					</div>

					<div id="searchBar">

						<div id="urlBox" >
							<input
							id="inputUrl"
							type='url'
							name='url'
							value={this.props.url}
							placeholder='https://github.com/urlAlRepo'
							onChange={ this.handleFieldChange } />
						</div>

						<div id="submitBox" className="text-center" onClick={ this.handleSubmit }>
							<span className="glyphicon glyphicon-search"></span>
						</div>

					</div>


					{StatusBox}


				</div>

			</div>

		</div>
		)
	}
}

const mapStateToProps = state => ({
	url: state.repoInfo.url,
	id: state.repoInfo.id,
	totalTests: state.repoInfo.total_tests,
	passedTest: state.repoInfo.passed_tests,
	status: state.status,
	vulnerabilities: state.vulnerabilities
});

const mapDispatchToProps = {
	loadUrl,
	checkUrl,
	checkStatus,
	checkResults,
	setStatus
}

export default connect(mapStateToProps, mapDispatchToProps)(SearchBar);