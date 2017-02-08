import React, { PropTypes } from 'react';
import {Link} from 'react-router';

const HistoryListItem = () => (
	<div
		style={{borderTop: 'solid 1px rgba(54, 54, 54, 0.5)',
			width: '100%',
			margin: 'auto'}} 
		className="row">

		<div className="col-xs-12 col-ms-8">
			repo/github.com
		</div>
		<div className="col-xs-6 col-ms-2">
			rm
		</div>
		<div className="col-xs-6 col-ms-2">
			3/5
		</div>
	</div>
)

export default HistoryListItem;