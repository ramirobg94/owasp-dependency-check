import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { setFilterLevel, setFilterOrder } from '../../modules/filter';

import ResultListItem from './resultListItem';

class ResultList extends Component{

	constructor(props){
		super(props);
		this.setFilterOrder = this.setFilterOrder.bind(this);
		this.setFilterLevels = this.setFilterLevels.bind(this);
	}

	setFilterOrder(value){
		this.props.setFilterOrder(value)
	}

	setFilterLevels(value){
		this.props.setFilterLevel(value)
	}

	render(){

		let levelsToOrder = [];

		if(this.props.filterOrder){
		 	levelsToOrder = ['low','medium','high', 'unknown'];
		}else{
			levelsToOrder = ['high','medium','low', 'unknown'];
		}

		let vulnerabilitiesFiltered = []

		if( this.props.filterLevels.length > 0){
			vulnerabilitiesFiltered = this.props.vulnerabilities.filter( (v) => {
				//console.log(this.props.filterLevels.indexOf(v.severity));
				return this.props.filterLevels.indexOf(v.severity) >= 0;
			})
		}

		const vulnerabilitiesOrdered = vulnerabilitiesFiltered.sort( (a,b) => {
			if(levelsToOrder.indexOf(a.severity) > levelsToOrder.indexOf(b.severity)){
				return 1;
			}
			if(levelsToOrder.indexOf(a.severity) < levelsToOrder.indexOf(b.severity)){
				return -1;
			}
			return 0;
		});

		const resultsListItems = vulnerabilitiesOrdered.map( (v,i) => 
				<ResultListItem 
					key={i} 
					severity={v.severity} 
					library={v.product}
					version={v.version}
					description={v.description}
					/>
			)

		return(
			<div style={{
				display: (this.props.status == 5 ? 'block' : 'none' ),
				height: '80px',
				boxShadow: '0px 5px 5px rgba(84, 84, 84, 0.52)',
				background: 'rgba(181, 229, 249, 0.5)',
				zIndex: 400}}>

				<div style={{ height: '80px', display: 'flex'}}>
					<div style={{ display: 'flex', margin: 'auto'}}>

						<button className="filter filterLeft"
							style={{ background :this.props.filterLevels.indexOf('low') >= 0 ? '#86c82d' : ''}}
							onClick={ () => {this.setFilterLevels('low')} }>
							low
						</button>
						<button className="filter filterMid"
							style={{ background :this.props.filterLevels.indexOf('medium') >= 0 ? '#86c82d' : ''}}
							onClick={ () => {this.setFilterLevels('medium')} }>
							medium
						</button>
						<button className="filter filterMid"
							style={{ background :this.props.filterLevels.indexOf('high') >= 0 ? '#86c82d' : ''}}
							onClick={ () => {this.setFilterLevels('high')} }>
							high
						</button>
						<button className="filter filterRight"
							style={{ background :this.props.filterLevels.indexOf('unknown') >= 0 ? '#86c82d' : ''}}
							onClick={ () => {this.setFilterLevels('unknown')} }>
							unknown
						</button>
					</div>

					<div style={{ display: 'flex', margin: 'auto'}}>
						<button className="filter filterLeft"
							style={{ background :this.props.filterOrder == 0 ? '#86c82d' : ''}}
							onClick={ () => {this.setFilterOrder(0)} }>
							descendente
						</button>
						<button className="filter filterRight"
							style={{ background :this.props.filterOrder == 1 ? '#86c82d' : ''}}
							onClick={ () => {this.setFilterOrder(1)} }>
							ascendente
						</button>
					</div>

				</div>

				<div style={{   
					height: 'calc(100vh - 200px)',
					overflow: 'scroll'}}>

					{resultsListItems}

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
		vulnerabilities: state.vulnerabilities,
		filterLevels: state.filter.levels,
		filterOrder: state.filter.order
	});

	const mapDispatchToProps = {
		setFilterLevel,
		setFilterOrder
	}

	export default connect(mapStateToProps, mapDispatchToProps)(ResultList);