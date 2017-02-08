import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

class Resume extends Component{
	constructor(props){
		super(props);
		this.handleFieldChange = this.handleFieldChange.bind(this);
	}

	handleFieldChange(e){
		this.props.saveDetails({
	      	[e.target.name]: e.target.value
    	});
	}


	render(){

		var vulsFiltered = this.props.vulnerabilities.filter((v) => v.severity != 'unknown')
		
		var sum = vulsFiltered.reduce((sum, vf)=>{
			if(vf.severity == 'low'){
				return sum + 1;
			}else if(vf.severity == 'medium'){
				return sum + 3;
			}else if(vf.severity == 'high'){
				return sum + 5;
			}else{
				return 0;
			}
		}, 0);
		
		const mean = Math.ceil(sum / vulsFiltered.length);
		
		const colors = ['#86c82d','#fdbd2c','#fdbd2c','#f67f1e','#c8175e','#c8175e'];
		const color = colors[mean];
		return(
			<div id="resumenBox">
				<div>
					<h2 style={{fontSize: '1.5em'}}>{this.props.urlProject}</h2>
				 	<h3 style={{fontSize: '1.2em'}}> Id: {this.props.idProject} </h3>
				</div>
				<div style={{ display: 'flex',flexDirection: 'row'}}>
					<div id='bola' style={{background: color}}>
						<h1>{mean}/5</h1>
					</div>
					<div style={{flex:1, textAlign: 'center'}}>
						<p> Un total de {this.props.totalTests} {this.props.totalTests == 1 ? 'herramienta ejecutada' : 'herramientas ejecutadas' }</p>
					 	<p> {this.props.vulnerabilities.length} {this.props.vulnerabilities.length == 1 ? 'vulnerabilidad encontrada' : 'vulnerabilidades encontradas' }</p>
						<div id="btnShowMore" onClick={this.props.showResults}>
							Ver detalle
						</div>
					</div>
				</div>
			</div>
		)
	}
}

/*
Landing.propTypes = {

}

const mapStateToProps = state => ({

});

const mapDispatchToProps = {

}*/

export default Resume;
//export default connect(mapStateToProps, mapDispatchToProps)(Landing);