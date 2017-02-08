import React from 'react';
import ReactDOM from 'react-dom';
import configureStore from './configureStore';
import { Provider } from 'react-redux';

import DepChecker from './components/index';
const store = configureStore();

ReactDOM.render(<Provider store={ store }><DepChecker/></Provider>,
  document.getElementById('app'));