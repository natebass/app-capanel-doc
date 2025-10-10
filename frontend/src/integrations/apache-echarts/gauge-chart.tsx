import * as echarts from 'echarts';
import { useEffect, useRef } from 'react';

// Define the component and accept optional props for customization
const EchartsGaugeChart = ({
	value = 0.7,
	name = 'Grade Rating',
	title = 'Grade Rating',
}) => {
	const chartRef = useRef(null);

	useEffect(() => {
		// Initialize the chart instance on the referenced div
		const myChart = echarts.init(chartRef.current);

		const option = {
			series: [
				{
					type: 'gauge',
					startAngle: 180,
					endAngle: 0,
					center: ['50%', '75%'],
					radius: '90%',
					min: 0,
					max: 1,
					splitNumber: 10,
					axisLine: {
						lineStyle: {
							width: 6,
							color: [
								[0.2, '#FF6E76'],
								[0.4, '#FFBB78'],
								[0.6, '#FDDD60'],
								[0.8, '#7CFFB2'],
								[1, '#58D9F9'],
							],
						},
					},
					pointer: {
						icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
						length: '12%',
						width: 20,
						offsetCenter: [0, '-60%'],
						itemStyle: {
							color: 'auto',
						},
					},
					axisTick: {
						length: 12,
						lineStyle: {
							color: 'auto',
							width: 2,
						},
					},
					splitLine: {
						length: 20,
						lineStyle: {
							color: 'auto',
							width: 5,
						},
					},
					axisLabel: {
						color: '#464646',
						fontSize: 20,
						distance: -60,
						rotate: 'tangential',
						formatter: (value: number) => {
							if (value === 0.9) return 'Blue';
							if (value === 0.7) return 'Green';
							if (value === 0.5) return 'Yellow';
							if (value === 0.3) return 'Orange';
							if (value === 0.1) return 'Red';
							return '';
						},
					},
					title: {
						offsetCenter: [0, '-10%'],
						fontSize: 20,
						// Use the title from props
						name: title,
					},
					detail: {
						fontSize: 30,
						offsetCenter: [0, '-35%'],
						valueAnimation: true,
						formatter: (value: number) => {
							// return Math.round(value * 100) + '';
							if (value < 0.21) {
								return 'Red';
							} else if (value < 0.41) {
								return 'Orange';
							} else if (value < 0.61) {
								return 'Yellow';
							} else if (value < 0.71) {
								return 'Green (mid)';
							} else if (value < 0.81) {
								return 'Green';
							} else if (value < 1) {
								return 'Blue';
							} else {
								return '';
							}
						},
						color: 'inherit',
					},
					data: [
						{
							// Use the value from props
							value: value,
							// Use the name from props
							name: name,
						},
					],
				},
			],
		};

		// Set the option and resize listener
		myChart.setOption(option);

		const handleResize = () => myChart.resize();
		window.addEventListener('resize', handleResize);

		// Clean up the chart instance and event listener when the component unmounts
		return () => {
			myChart.dispose();
			window.removeEventListener('resize', handleResize);
		};
	}, [value, name, title]); // Re-run the effect if these props change

	return <div ref={chartRef} style={{ width: '100%', height: '400px' }} />;
};

export default EchartsGaugeChart;
