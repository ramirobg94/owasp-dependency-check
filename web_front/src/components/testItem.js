
import React, { PropTypes } from 'react';

const TestItem = ({title, passed, id}) => (

	<div style={{opacity: passed ? 1 : 0.8 , display: 'flex', marginTop: 20}}>
		<div style={{width: '50%',
    maxWidth: 120,
    marginLeft: 'auto'}}>
		{passed ?
			<span style={{fontSize: 70}} className={'glyphicon glyphicon-ok-circle'}></span> :
			<span style={{fontSize: 70}} className={'glyphicon glyphicon-refresh'}></span> 
		}
		
		 </div>
		 <div style={{
    width: '50%',
    maxWidth: 120,
    marginRight: 'auto'}}>
			 <h2>
			 	test {id}
			 </h2>
		 </div>
	</div>

)

export default TestItem;