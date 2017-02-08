import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import TestItem from './testItem';

class Status extends Component{
	constructor(props){
		super(props);
	}

	componentDidMount(){
		this._interval = setInterval(() => {
     	console.log("call")
      this.props.checkStatus();
    }, 1500)
		
	}

	componentDidUpdate(){
		if(this.props.status > 2){
			console.log("clean interval")
			clearInterval(this._interval);
		}
	}

	componentWillUnmount(){
		console.log("clean interval")
		clearInterval(this._interval);
	}
	render(){
		
		var test =[];

		
			for(var i = 0; i < this.props.totalTests; i++){
					test.push(<TestItem  key={i} id={i} title="si" passed={i < this.props.passedTest }/>);
			}
		
		
		return(
			<div id="resumenBox" className="text-center" style={{display: (this.props.status > 0 && this.props.status < 3 )? 'block' : 'none'}}>
					<h2>Comprobando...</h2>
					{test}
			</div>
		)
	}
}

export default Status;