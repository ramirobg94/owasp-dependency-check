import React, { Component, PropTypes } from 'react';



class ResultListItem extends Component{
	constructor(props){
		super(props);
		this.state = {flipped: false};
	}

	render(){
		return(

<div className={'vulnerabilityCard row ' 
	+ (this.props.severity == 'low' ? 
			'cardLow' 
			: ( this.props.severity == 'medium' ? 
				'cardMedium' 
				: ( this.props.severity == 'high' ? 
					'cardHigh' : '' )
				)) + ' '+(this.state.flipped ? 'flipped' : '')
		}

		onClick={(e) => this.setState({flipped: !this.state.flipped})}>
		<div className="front" style={{display: (this.state.flipped ? 'none' : 'block')}}>
			<div className="col-xs-12 col-sm-12 text-center">
				library:{this.props.library}
			</div>
			<div className="col-xs-12 col-sm-12 text-center">
				version:{this.props.version}
			</div>
			<div className="col-xs-12 col-sm-6 text-center">
				Criticidad: {this.props.severity}
			</div>
			<div className="col-xs-12 col-sm-6 text-center">
				
			</div>
		</div>

		<div className="back" style={{display: (this.state.flipped ? 'block' : 'none')}}>
			<div className="col-xs-12 col-sm-12 text-center">
				Description:
			</div>
			<div className="col-xs-12 col-sm-12 text-center">
				{this.props.description}	
			</div>
		</div>

	</div>

			);
	}
}
	

export default ResultListItem;


